import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import PyPDF2
import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from functools import lru_cache
from .models import (
    Persona, JobToBeDone, ExtractedSection, SubsectionAnalysis
)

class DocumentProcessor:
    def __init__(self):
        """Initialize the lightweight document processor."""
        # Load spaCy for text processing (smaller model)
        try:
            self.nlp = spacy.load("en_core_web_sm", disable=['ner', 'parser'])  # Disable unused components
        except OSError:
            print("Please install spacy model: python -m spacy download en_core_web_sm")
            raise
        
        # Use TF-IDF with optimized settings
        self.vectorizer = TfidfVectorizer(
            max_features=500,  # Reduced from 1000 for faster processing
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.95,  # Ignore terms that appear in >95% of docs
            min_df=2,     # Ignore terms that appear in <2 docs
        )
        
        # Cache for processed sections
        self._section_cache = {}

    @lru_cache(maxsize=100)
    def _is_heading(self, text: str) -> bool:
        """Determine if text is likely a heading (cached)."""
        text = text.strip()
        if not text or len(text) > 200:
            return False
            
        patterns = [
            r'^[0-9]+\.',
            r'^[0-9]+\.[0-9]+',
            r'^[A-Z][A-Z\s]+$',
            r'^(Chapter|Section|Part)\s+[0-9]+',
            r'^(Abstract|Introduction|Conclusion|References|Methodology|Results|Discussion)$',
        ]
        
        # Combine patterns for single regex check
        combined_pattern = '|'.join(f'({p})' for p in patterns)
        if re.match(combined_pattern, text, re.IGNORECASE):
            return True
            
        return len(text.split()) <= 6 and text.endswith(':')

    def _extract_document_sections(self, pdf_path: Path) -> List[Dict]:
        """Extract sections from a PDF document with optimizations."""
        cache_key = str(pdf_path)
        if cache_key in self._section_cache:
            return self._section_cache[cache_key]
            
        sections = []
        current_section = None
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text_buffer = []
                
                # Process pages in batches for better memory usage
                batch_size = 5
                for i in range(0, len(reader.pages), batch_size):
                    batch_pages = reader.pages[i:i + batch_size]
                    
                    for page_num, page in enumerate(batch_pages, i + 1):
                        try:
                            text = page.extract_text()
                            if not text.strip():
                                continue
                                
                            # Process text with spaCy efficiently
                            doc = self.nlp(text)
                            
                            for sent in doc.sents:
                                sent_text = sent.text.strip()
                                if not sent_text:
                                    continue
                                    
                                if self._is_heading(sent_text):
                                    if current_section and current_section['content'].strip():
                                        sections.append(current_section)
                                    
                                    current_section = {
                                        'title': sent_text,
                                        'content': '',
                                        'page_number': page_num,
                                        'relevance_score': 0.0,
                                        'key_points': [],
                                        'parent_section': None
                                    }
                                elif current_section:
                                    current_section['content'] += sent_text + ' '
                            
                            # Create generic section if needed
                            if not current_section and text.strip():
                                current_section = {
                                    'title': f'Content from Page {page_num}',
                                    'content': text.strip(),
                                    'page_number': page_num,
                                    'relevance_score': 0.0,
                                    'key_points': [],
                                    'parent_section': None
                                }
                                
                        except Exception as e:
                            print(f"Error processing page {page_num}: {str(e)}")
                            continue
                
                # Add the last section
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
        """Rank sections based on relevance using TF-IDF similarity with optimizations."""
        if not sections:
            return []
            
        # Create focused context string
        context = f"{job.task} {persona.role}"
        if job.objectives:
            context += " " + " ".join(job.objectives[:3])  # Use only top 3 objectives
        
        # Prepare texts efficiently
        section_texts = [
            f"{section['title']} {section['content'][:500]}"  # Reduced from 1000
            for section in sections
        ]
        
        all_texts = [context] + section_texts
        
        try:
            # Vectorize and calculate similarities
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            
            # Update sections efficiently
            for i, section in enumerate(sections):
                section['relevance_score'] = max(0.0, float(similarities[i]))
                section['key_points'] = self._extract_key_points(section['content'][:1000])
                
        except Exception as e:
            print(f"Error in relevance ranking: {str(e)}")
            for i, section in enumerate(sections):
                section['relevance_score'] = max(0.0, 0.5 - i * 0.1)
                section['key_points'] = self._extract_key_points(section['content'][:1000])
        
        return sorted(sections, key=lambda x: x['relevance_score'], reverse=True)

    @lru_cache(maxsize=1000)
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content (cached)."""
        if not content:
            return []
            
        try:
            doc = self.nlp(content[:2000])  # Limit content length for processing
            key_points = []
            
            key_indicators = {
                'important', 'key', 'significant', 'essential', 'critical',
                'results show', 'we found', 'demonstrates', 'proves',
                'conclusion', 'summary', 'main', 'primary'
            }
            
            for sent in doc.sents:
                sent_text = sent.text.strip()
                if (20 < len(sent_text) < 300 and  # Length check
                    any(indicator in sent_text.lower() for indicator in key_indicators)):
                    key_points.append(sent_text)
                    if len(key_points) >= 5:  # Early exit after finding 5 points
                        break
            
            return key_points
        except Exception:
            return []

    def process_document(self, pdf_path: Path, persona: Persona, job: JobToBeDone):
        """Process a single document and return ranked sections."""
        sections = self._extract_document_sections(pdf_path)
        ranked_sections = self._rank_sections_by_relevance(sections, persona, job)
        
        class ProcessingResult:
            def __init__(self, sections):
                self.sections = sections
        
        return ProcessingResult(ranked_sections) 