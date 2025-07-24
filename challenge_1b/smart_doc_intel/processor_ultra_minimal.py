import time
import re
from typing import List, Dict
from pathlib import Path
import PyPDF2
from .models import Persona, JobToBeDone

class DocumentProcessor:
    def __init__(self):
        """Ultra-minimal processor for maximum speed."""
        pass

    def _is_heading(self, text: str) -> bool:
        """Simple heading detection."""
        text = text.strip()
        if not text or len(text) > 200:
            return False
            
        # Basic patterns
        if re.match(r'^[0-9]+\.', text) or re.match(r'^[A-Z][A-Z\s]+$', text):
            return True
        if text.lower() in ['introduction', 'conclusion', 'summary', 'abstract', 'methodology']:
            return True
        return len(text.split()) <= 6 and text.endswith(':')

    def _simple_relevance_score(self, text: str, context: str) -> float:
        """Ultra-simple relevance scoring without ML."""
        if not text or not context:
            return 0.0
        
        text_lower = text.lower()
        context_words = context.lower().split()
        
        score = 0.0
        for word in context_words:
            if len(word) > 3 and word in text_lower:
                score += 1.0
        
        # Normalize by text length
        return min(1.0, score / max(1, len(text.split()) / 10))

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points using simple heuristics."""
        if not content:
            return []
        
        sentences = re.split(r'[.!?]', content)
        key_points = []
        
        for sentence in sentences[:10]:  # Only check first 10 sentences
            sentence = sentence.strip()
            if (20 < len(sentence) < 150 and
                any(word in sentence.lower() for word in ['important', 'key', 'essential', 'main'])):
                key_points.append(sentence)
                if len(key_points) >= 3:
                    break
        
        return key_points

    def _extract_document_sections(self, pdf_path: Path) -> List[Dict]:
        """Extract sections with minimal processing."""
        sections = []
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                current_section = None
                
                # Process only first 5 pages for speed
                for page_num, page in enumerate(reader.pages[:5], 1):
                    try:
                        text = page.extract_text()
                        if not text.strip():
                            continue
                        
                        # Split into simple sentences
                        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
                        
                        for sentence in sentences[:20]:  # Limit sentences per page
                            if self._is_heading(sentence):
                                if current_section:
                                    sections.append(current_section)
                                
                                current_section = {
                                    'title': sentence,
                                    'content': '',
                                    'page_number': page_num,
                                    'relevance_score': 0.0,
                                    'key_points': [],
                                    'parent_section': None
                                }
                            elif current_section and len(current_section['content']) < 500:
                                current_section['content'] += sentence + '. '
                        
                        # Create generic section if none found
                        if not current_section:
                            current_section = {
                                'title': f'Page {page_num} Content',
                                'content': text[:300],  # Limit content
                                'page_number': page_num,
                                'relevance_score': 0.0,
                                'key_points': [],
                                'parent_section': None
                            }
                            sections.append(current_section)
                            current_section = None
                            
                    except Exception:
                        continue
                
                if current_section:
                    sections.append(current_section)
                    
        except Exception as e:
            # Fallback section
            sections = [{
                'title': f'Document: {pdf_path.name}',
                'content': f'Error: {str(e)}',
                'page_number': 1,
                'relevance_score': 0.5,
                'key_points': [],
                'parent_section': None
            }]
        
        return sections[:10]  # Limit to 10 sections max

    def process_document(self, pdf_path: Path, persona: Persona, job: JobToBeDone):
        """Process document with minimal overhead."""
        sections = self._extract_document_sections(pdf_path)
        
        # Simple context for relevance
        context = f"{job.task} {persona.role}"
        
        # Score and rank sections
        for section in sections:
            section['relevance_score'] = self._simple_relevance_score(
                section['title'] + ' ' + section['content'], context
            )
            section['key_points'] = self._extract_key_points(section['content'])
        
        # Sort by relevance
        sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        class ProcessingResult:
            def __init__(self, sections):
                self.sections = sections
        
        return ProcessingResult(sections) 