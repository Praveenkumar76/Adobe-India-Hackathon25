import time
import re
from typing import List, Dict, Optional
from pathlib import Path
import PyPDF2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache
from .models import Persona, JobToBeDone

class DocumentProcessor:
    def __init__(self):
        """Initialize the minimal document processor."""
        # Use TF-IDF for text analysis
        self.vectorizer = TfidfVectorizer(
            max_features=300,  # Very small for speed
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.95,
            min_df=1,
        )
        self._section_cache = {}

    @lru_cache(maxsize=100)
    def _is_heading(self, text: str) -> bool:
        """Determine if text is likely a heading."""
        text = text.strip()
        if not text or len(text) > 200:
            return False
            
        # Simple patterns for headings
        patterns = [
            r'^[0-9]+\.',
            r'^[0-9]+\.[0-9]+',
            r'^[A-Z][A-Z\s]+$',
            r'^(Chapter|Section|Part)\s+[0-9]+',
            r'^(Abstract|Introduction|Conclusion|References|Methodology|Results|Discussion)$',
        ]
        
        combined_pattern = '|'.join(f'({p})' for p in patterns)
        if re.match(combined_pattern, text, re.IGNORECASE):
            return True
            
        return len(text.split()) <= 6 and text.endswith(':')

    def _simple_sentence_split(self, text: str) -> List[str]:
        """Simple sentence splitting without spaCy."""
        # Split on periods, exclamation marks, question marks
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

    def _extract_document_sections(self, pdf_path: Path) -> List[Dict]:
        """Extract sections from PDF without spaCy."""
        cache_key = str(pdf_path)
        if cache_key in self._section_cache:
            return self._section_cache[cache_key]
            
        sections = []
        current_section = None
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(reader.pages[:10], 1):  # Limit to first 10 pages for speed
                    try:
                        text = page.extract_text()
                        if not text.strip():
                            continue
                            
                        # Simple sentence splitting
                        sentences = self._simple_sentence_split(text)
                        
                        for sentence in sentences:
                            if self._is_heading(sentence):
                                if current_section and current_section['content'].strip():
                                    sections.append(current_section)
                                
                                current_section = {
                                    'title': sentence,
                                    'content': '',
                                    'page_number': page_num,
                                    'relevance_score': 0.0,
                                    'key_points': [],
                                    'parent_section': None
                                }
                            elif current_section:
                                current_section['content'] += sentence + '. '
                        
                        # Create generic section if needed
                        if not current_section and text.strip():
                            current_section = {
                                'title': f'Content from Page {page_num}',
                                'content': text.strip()[:1000],  # Limit content
                                'page_number': page_num,
                                'relevance_score': 0.0,
                                'key_points': [],
                                'parent_section': None
                            }
                            
                    except Exception as e:
                        print(f"Error processing page {page_num}: {str(e)}")
                        continue
                
                if current_section and current_section['content'].strip():
                    sections.append(current_section)
                    
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            sections = [{
                'title': f'Document Content - {pdf_path.name}',
                'content': f'Error processing document: {str(e)}',
                'page_number': 1,
                'relevance_score': 0.0,
                'key_points': [],
                'parent_section': None
            }]
        
        self._section_cache[cache_key] = sections
        return sections

    def _rank_sections_by_relevance(self, sections: List[Dict], persona: Persona, job: JobToBeDone) -> List[Dict]:
        """Rank sections using TF-IDF similarity."""
        if not sections:
            return []
            
        # Create context
        context = f"{job.task} {persona.role}"
        if job.objectives:
            context += " " + " ".join(job.objectives[:2])  # Use only top 2 objectives
        
        # Prepare texts
        section_texts = [
            f"{section['title']} {section['content'][:300]}"  # Even smaller chunks
            for section in sections
        ]
        
        all_texts = [context] + section_texts
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            
            for i, section in enumerate(sections):
                section['relevance_score'] = max(0.0, float(similarities[i]))
                section['key_points'] = self._extract_key_points(section['content'][:500])
                
        except Exception as e:
            print(f"Error in relevance ranking: {str(e)}")
            for i, section in enumerate(sections):
                section['relevance_score'] = max(0.0, 0.8 - i * 0.1)
                section['key_points'] = self._extract_key_points(section['content'][:500])
        
        return sorted(sections, key=lambda x: x['relevance_score'], reverse=True)

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points without spaCy."""
        if not content:
            return []
            
        sentences = self._simple_sentence_split(content)
        key_points = []
        
        key_indicators = {
            'important', 'key', 'significant', 'essential', 'critical',
            'summary', 'main', 'primary', 'conclusion'
        }
        
        for sentence in sentences:
            if (20 < len(sentence) < 200 and  # Length check
                any(indicator in sentence.lower() for indicator in key_indicators)):
                key_points.append(sentence)
                if len(key_points) >= 3:  # Limit to 3 points
                    break
        
        return key_points

    def process_document(self, pdf_path: Path, persona: Persona, job: JobToBeDone):
        """Process a single document."""
        sections = self._extract_document_sections(pdf_path)
        ranked_sections = self._rank_sections_by_relevance(sections, persona, job)
        
        class ProcessingResult:
            def __init__(self, sections):
                self.sections = sections
        
        return ProcessingResult(ranked_sections) 