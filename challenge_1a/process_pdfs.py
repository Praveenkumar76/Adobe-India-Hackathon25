#!/usr/bin/env python3
"""
Smart PDF Document Analyzer
Adobe India Hackathon 2025

A system that can "read" any PDF document and understand its structure like a human would,
then output that understanding in a machine-readable format.

This isn't just text extraction - it's document intelligence that recognizes:
- "This looks like a main title"
- "This seems like a major section heading" 
- "This appears to be a sub-section under that major heading"
- "This content appears on page X"

The system combines multiple intelligence layers to understand document structure
the same way a human would when quickly scanning a document.
"""

import fitz  # PyMuPDF
import json
import os
import sys
from pathlib import Path
import re
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    """
    Smart PDF Document Analyzer - The "Document Understanding Brain"
    
    This class implements human-like document understanding by combining multiple
    intelligence layers to recognize document structure patterns just like a human would.
    
    Key Intelligence Components:
    1. Visual Pattern Recognition - Analyzes typography and layout
    2. Contextual Understanding - Considers relationships between text elements  
    3. Structural Intelligence - Recognizes academic and professional conventions
    4. Multi-Factor Decision Making - Weighs multiple signals for accuracy
    """
    
    def __init__(self):
        # Human-like understanding parameters
        self.font_size_threshold = 2.0  # Typography significance threshold
        
        # Academic and professional document conventions that humans recognize
        self.common_heading_patterns = [
            # English patterns
            r'^chapter\s+\d+',           # "Chapter 1", "Chapter 2" 
            r'^\d+\.\s',                 # "1. Introduction", "2. Methods"
            r'^\d+\.\d+\s',             # "1.1 Overview", "2.3 Analysis"  
            r'^\d+\.\d+\.\d+\s',        # "1.1.1 Details", "2.3.1 Subsection"
            r'^[A-Z][^a-z]*$',          # "INTRODUCTION", "METHODOLOGY" (all caps)
            r'^[A-Z][a-z]+\s[A-Z]',     # "Data Collection", "Statistical Analysis" (title case)
            r'^abstract$',               # Academic papers
            r'^introduction$',           # Common section names
            r'^conclusion$',
            r'^references$',
            r'^bibliography$',
            
            # Japanese patterns
            r'^第\d+章',                 # "第1章" (Chapter 1)
            r'^[\d０-９]+．',            # "1．" (Japanese full-width numbers)
            r'^[\d０-９]+．[\d０-９]+',   # "1．1" (Section 1.1)
            r'^[\d０-９]+．[\d０-９]+．[\d０-９]+', # "1．1．1" (Section 1.1.1)
            r'^はじめに',                # "はじめに" (Introduction)
            r'^まとめ',                  # "まとめ" (Summary/Conclusion)
            r'^参考文献',                # "参考文献" (References)
            
            # Hindi patterns
            r'^\d+\.\s+[\u0900-\u097F]+',  # "1. परिचय" (1. Introduction)
            r'^अध्याय\s+\d+',              # "अध्याय 1" (Chapter 1)
            r'^परिचय$',                    # "परिचय" (Introduction)
            r'^निष्कर्ष$',                 # "निष्कर्ष" (Conclusion)
            r'^संदर्भ$',                   # "संदर्भ" (References)
            
            # Universal patterns (work across languages)
            r'^[IVX]+\.',                # Roman numerals
            r'^[A-Z]\.',                 # "A.", "B." style headings
            r'^[A-Z]\d+',                # "A1", "B2" style headings
            r'^[-–—•]\s',                # Bullet points
            r'^[①-⑳]',                   # Circled numbers (common in Asian docs)
            r'^PART\s+[A-Z0-9]',         # "PART A", "PART 1"
            r'^SECTION\s+[A-Z0-9]',      # "SECTION A", "SECTION 1"
        ]
    
    def extract_text_with_formatting(self, page) -> List[Dict]:
        """Extract text with detailed formatting information."""
        blocks = page.get_text("dict")
        text_elements = []
        
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["text"].strip():
                            text_elements.append({
                                "text": span["text"].strip(),
                                "font": span["font"],
                                "size": span["size"],
                                "flags": span["flags"],
                                "bbox": span["bbox"],
                                "page": page.number + 1
                            })
        
        return text_elements

    def merge_broken_headings(self, elements: List[Dict]) -> List[Dict]:
        """
        Merge text elements that appear to be part of the same heading.
        This handles cases where headings are split across lines.
        
        Args:
            elements: List of text elements with formatting information
            
        Returns:
            List of merged text elements
        """
        if not elements:
            return []
            
        merged = []
        i = 0
        while i < len(elements):
            current = elements[i]
            
            # Look ahead to see if next element should be merged
            if i + 1 < len(elements):
                next_elem = elements[i + 1]
                
                # Check if elements should be merged based on:
                # 1. Same font and size (formatting consistency)
                # 2. Close vertical position (within reasonable line spacing)
                # 3. Same page
                # 4. Current text doesn't end with sentence-ending punctuation
                vertical_gap = abs(next_elem["bbox"][1] - current["bbox"][3])
                same_format = (current["font"] == next_elem["font"] and 
                             abs(current["size"] - next_elem["size"]) < 0.1)
                same_page = current["page"] == next_elem["page"]
                no_end_punct = not current["text"].strip().endswith(('.', '!', '?', ':', ';'))
                reasonable_gap = vertical_gap < current["size"] * 1.5  # Max 1.5x font size gap
                
                if (same_format and same_page and no_end_punct and reasonable_gap):
                    # Merge the elements
                    merged_text = f"{current['text']} {next_elem['text']}"
                    merged.append({
                        "text": merged_text,
                        "font": current["font"],
                        "size": current["size"],
                        "flags": current["flags"],
                        "bbox": (
                            min(current["bbox"][0], next_elem["bbox"][0]),  # x0
                            current["bbox"][1],                             # y0
                            max(current["bbox"][2], next_elem["bbox"][2]),  # x1
                            next_elem["bbox"][3]                            # y1
                        ),
                        "page": current["page"]
                    })
                    i += 2  # Skip the next element since we merged it
                    continue
                    
            merged.append(current)
            i += 1
            
        return merged
    
    def analyze_font_structure(self, all_elements: List[Dict]) -> Dict[str, Any]:
        """
        Analyze the font structure of the document to identify base font size and heading thresholds.
        
        Returns:
            Dict containing base_font_size, heading_thresholds, and font_analysis
        """
        from collections import Counter
        
        # Get all font sizes
        font_sizes = [elem["size"] for elem in all_elements]
        font_size_counter = Counter(font_sizes)
        
        # The base font size is typically the most common font size in the document
        # This represents the body text
        base_font_size = font_size_counter.most_common(1)[0][0]
        
        # Calculate HTML heading size thresholds based on base font size
        h1_threshold = base_font_size * 2.0     # 2em
        h2_threshold = base_font_size * 1.5     # 1.5em  
        h3_threshold = base_font_size * 1.17    # 1.17em
        
        # Find unique font sizes and categorize them
        unique_sizes = sorted(set(font_sizes), reverse=True)
        
        # Categorize fonts by their likely heading level based on HTML standards
        h1_sizes = [size for size in unique_sizes if size >= h1_threshold]
        h2_sizes = [size for size in unique_sizes if h2_threshold <= size < h1_threshold]
        h3_sizes = [size for size in unique_sizes if h3_threshold <= size < h2_threshold]
        body_sizes = [size for size in unique_sizes if size < h3_threshold]
        
        logger.info(f"Font analysis - Base: {base_font_size:.1f}pt, H1: ≥{h1_threshold:.1f}pt, H2: {h2_threshold:.1f}-{h1_threshold:.1f}pt, H3: {h3_threshold:.1f}-{h2_threshold:.1f}pt")
        
        return {
            "base_font_size": base_font_size,
            "h1_threshold": h1_threshold,
            "h2_threshold": h2_threshold, 
            "h3_threshold": h3_threshold,
            "h1_sizes": h1_sizes,
            "h2_sizes": h2_sizes,
            "h3_sizes": h3_sizes,
            "body_sizes": body_sizes,
            "unique_sizes": unique_sizes
        }

    def is_likely_heading(self, element: Dict, font_analysis: Dict, common_fonts: set) -> bool:
        """
        Determine if an element is likely a heading using HTML font size standards.
        
        Uses exact HTML heading ratios:
        - H1: 2em (200% of base font size)
        - H2: 1.5em (150% of base font size) 
        - H3: 1.17em (117% of base font size)
        """
        text = element["text"]
        font_size = element["size"]
        font_name = element["font"]
        flags = element["flags"]
        bbox = element["bbox"]
        
        # Skip very short text (likely not headings)
        if len(text.strip()) < 3:
            return False
        
        # Skip very long text (likely paragraphs)
        if len(text.strip()) > 200:
            return False
            
        # Get font analysis data
        base_font_size = font_analysis["base_font_size"]
        h3_threshold = font_analysis["h3_threshold"]
        
        # Calculate exact font size ratio
        size_ratio = font_size / base_font_size if base_font_size > 0 else 1.0
        
        # PRIMARY FILTER: Font size must meet minimum heading threshold (H3 = 1.17em)
        if font_size < h3_threshold:
            # Exception: if it matches very strong heading patterns, allow smaller sizes
            strong_patterns = [
                r'^chapter\s+\d+',
                r'^\d+\.\s+(?![0-9])',  # "1. " not followed by number
                r'^\d+\.\d+\s+(?![0-9])',  # "1.1 " not followed by number  
                r'^\d+\.\d+\.\d+\s+',  # "1.1.1 "
                r'^[IVX]+\.\s+',  # Roman numerals
                r'^第\d+章',  # Japanese chapters
                r'^अध्याय\s+\d+',  # Hindi chapters
                r'^section\s+\d+',  # Section numbers
            ]
            
            if not any(re.match(pattern, text.lower()) for pattern in strong_patterns):
                return False
        
        # Text formatting flags
        is_bold = bool(flags & 16)  # fitz.TEXT_FONT_BOLD = 16
        is_italic = bool(flags & 8)  # fitz.TEXT_FONT_ITALIC = 8
        is_underlined = bool(flags & 4)  # fitz.TEXT_DECORATION_UNDERLINE = 4
        has_color = bool(flags & 1)  # fitz.TEXT_RENDER_MODE_FILL = 1
        
        # Special formatting score
        format_score = (is_bold or is_italic or is_underlined or has_color)
        
        # Font different from common body fonts
        font_score = font_name not in common_fonts
        
        # Pattern matching for common heading structures
        pattern_score = any(re.match(pattern, text.lower()) for pattern in self.common_heading_patterns)
        
        # Additional patterns for non-standard numbering
        extra_patterns = [
            r'^[A-Z]\.',                # "A.", "B." style
            r'^[A-Z]\d+',               # "A1", "B2" style
            r'^[IVX]+\.',               # Roman numerals
            r'^PART\s+[A-Z0-9]',        # "PART A", "PART 1"
            r'^SECTION\s+[A-Z0-9]',     # "SECTION A", "SECTION 1"
            r'^[-–—•]\s',               # Bullet points
            r'^[①-⑳]',                  # Circled numbers
            r'^appendix\s+[a-z]',       # "Appendix A"
            r'^figure\s+\d+',           # "Figure 1"
            r'^table\s+\d+',            # "Table 1"
        ]
        
        extra_pattern_score = any(re.match(pattern, text.lower()) for pattern in extra_patterns)
        
        # Title case or all caps
        case_score = text.isupper() or text.istitle()
        
        # Position analysis (headings often start at left margin or are centered)
        page_width = bbox[2] - bbox[0]  # width of text
        is_centered = abs((bbox[0] + bbox[2]) / 2 - page_width / 2) < 20
        starts_at_margin = bbox[0] < 72  # within 1 inch of left margin
        position_score = is_centered or starts_at_margin
        
        # Scoring system based on HTML heading size standards
        score = 0
        
        # Font size scoring based on exact HTML heading ratios
        if size_ratio >= 2.0:  # H1 threshold (2em)
            score += 5
        elif size_ratio >= 1.5:  # H2 threshold (1.5em)
            score += 4
        elif size_ratio >= 1.17:  # H3 threshold (1.17em)
            score += 3
        elif size_ratio >= 1.1:  # Slightly larger than body
            score += 1
        
        # Additional signals
        if is_bold: score += 2         # "That's bold" - good signal
        if format_score: score += 1    # "That has special formatting" - weak signal
        if font_score: score += 1      # "That font looks different" - weak signal
        if pattern_score: score += 3   # "That follows a heading pattern" - strong signal
        if extra_pattern_score: score += 2  # "That follows a special pattern" - good signal
        if case_score: score += 1      # "That's capitalized like a title" - weak signal
        if position_score: score += 1  # "That's positioned like a heading" - weak signal
        if is_underlined: score += 1   # "That's underlined" - weak signal
        if has_color: score += 1       # "That's in a different color" - weak signal
        
        # Decision threshold based on evidence strength
        if pattern_score or extra_pattern_score:
            # If it matches heading patterns, lower threshold
            min_score = 4
        else:
            # If no clear patterns, require strong formatting evidence
            min_score = 5
            
        return score >= min_score

    def classify_heading_level(self, element: Dict, font_analysis: Dict) -> str:
        """
        Intelligent Hierarchy Recognition using exact HTML heading size standards.
        
        Uses exact HTML heading ratios:
        - H1: 2em (200% of base font size) = 32px if base is 16px
        - H2: 1.5em (150% of base font size) = 24px if base is 16px
        - H3: 1.17em (117% of base font size) = 18.72px if base is 16px
        
        Returns:
            str: "H1", "H2", or "H3" based on analysis
        """
        text = element["text"].strip()
        font_size = element["size"]
        flags = element["flags"]
        
        # Get font analysis data
        base_font_size = font_analysis["base_font_size"]
        h1_threshold = font_analysis["h1_threshold"]
        h2_threshold = font_analysis["h2_threshold"]
        h3_threshold = font_analysis["h3_threshold"]
        
        # Calculate exact font size ratio
        size_ratio = font_size / base_font_size if base_font_size > 0 else 1.0
        
        # 1. Pattern-based level detection (most reliable - overrides font size)
        text_lower = text.lower()
        
        # Clear H1 indicators - Major sections
        if any([
            # Chapter patterns
            re.match(r'^chapter\s+\d+', text_lower),
            re.match(r'^第\d+章', text),  # Japanese chapter
            re.match(r'^अध्याय\s+\d+', text),  # Hindi chapter
            # Major section patterns (single level numbering)
            re.match(r'^\d+\.\s+(?![0-9])', text),  # "1. " not followed by number
            re.match(r'^section\s+\d+', text_lower),  # "Section 1", "Section 2"
            re.match(r'^[IVX]+\.\s+', text),  # Roman numerals
            # Common major section names
            text_lower in {'abstract', 'introduction', 'conclusion', 'references', 'bibliography',
                          'methodology', 'results', 'discussion', 'background', 'summary',
                          'acknowledgments', 'acknowledgements', 'executive summary',
                          'はじめに', 'まとめ', 'परिचय', 'निष्कर्ष'},
            # ALL CAPS major sections (short phrases only)
            text.isupper() and len(text) > 3 and len(text.split()) <= 4,
            # Part/Section markers
            re.match(r'^(?:part|section)\s+[A-Z0-9]', text_lower),
            re.match(r'^(?:part|section)\s+\d+:', text_lower),  # "Section 1:", "Part 2:"
            # Appendix
            re.match(r'^appendix\s+[a-z]', text_lower),
            # Analysis/Evaluation sections (common in academic papers)
            re.match(r'^analysis$', text_lower),
            re.match(r'^evaluation$', text_lower),
            re.match(r'^implementation$', text_lower),
            re.match(r'^related work$', text_lower),
            re.match(r'^literature review$', text_lower),
            # Number-only sections
            re.match(r'^\d+$', text) and len(text) <= 2,  # "1", "2", "3" etc.
        ]):
            return "H1"
            
        # Clear H2 indicators - Sub-sections
        if any([
            re.match(r'^\d+\.\d+\s+(?![0-9])', text),  # "1.1 " not followed by number
            re.match(r'^[A-Z]\.\s+', text),  # "A. "
            re.match(r'^[A-Z]\d+\.\s+', text),  # "A1. "
            # Subsection with parent reference
            re.match(r'^(?:section|part)\s+\d+\.\d+', text_lower),
            # Numbered subsections without dots
            re.match(r'^\d+\.\d+\s', text),  # "1.1 Something"
            # Letters for subsections
            re.match(r'^[a-z]\.\s+', text),  # "a. Something"
            re.match(r'^[a-z]\)\s+', text),  # "a) Something"
        ]):
            return "H2"
            
        # Clear H3 indicators - Sub-sub-sections
        if any([
            re.match(r'^\d+\.\d+\.\d+\s+', text),  # "1.1.1 "
            re.match(r'^[A-Z]\d+\.\d+\s+', text),  # "A1.1 "
            # Deep subsection patterns
            re.match(r'^(?:section|part)\s+\d+\.\d+\.\d+', text_lower)
        ]):
            return "H3"
            
        # 2. Font size based classification using EXACT HTML heading standards
        if font_size >= h1_threshold:  # 2em threshold
            return "H1"
        elif font_size >= h2_threshold:  # 1.5em threshold
            return "H2"
        elif font_size >= h3_threshold:  # 1.17em threshold
            return "H3"
        
        # 3. Fallback using font size ranking for edge cases
        unique_sizes = font_analysis["unique_sizes"]
        
        try:
            size_rank = unique_sizes.index(font_size)
            total_sizes = len(unique_sizes)
            
            # For documents with few distinct sizes
            if total_sizes <= 3:
                if size_rank == 0:
                    return "H1"
                elif size_rank == 1:
                    return "H2"
                else:
                    return "H3"
            else:
                # For documents with many sizes, be more selective
                if size_rank == 0:
                    return "H1"
                elif size_rank == 1:
                    return "H2"
                elif size_rank == 2:
                    return "H3"
                else:
                    return "H3"
                    
        except ValueError:
            return "H3"
        
        # 4. Final fallback
        return "H3"
    
    def extract_title(self, doc) -> str:
        """
        Smart Title Discovery
        
        Like a human who looks at a document and immediately identifies the title,
        this method uses multiple strategies:
        
        1. "Check the document properties" - metadata analysis
        2. "Look for the biggest, most prominent text at the top" - visual analysis  
        3. "Make sure it looks like a title, not just random big text" - validation
        
        Fallback gracefully if no clear title is found.
        """
        # Try metadata first
        metadata = doc.metadata
        if metadata.get("title") and metadata["title"].strip():
            return metadata["title"].strip()
        
        # Try first page - look for largest, prominent text
        if len(doc) == 0:
            return "Untitled Document"
        
        first_page = doc[0]
        text_elements = self.extract_text_with_formatting(first_page)
        
        if not text_elements:
            return "Untitled Document"
        
        # Find the largest font size on first page
        max_font_size = max(elem["size"] for elem in text_elements)
        
        # Look for title candidates (largest font, reasonable length)
        title_candidates = []
        for elem in text_elements:
            if (elem["size"] >= max_font_size - 1 and 
                len(elem["text"].strip()) > 5 and 
                len(elem["text"].strip()) < 100):
                title_candidates.append(elem)
        
        if title_candidates:
            return title_candidates[0]["text"].strip()
        
        return "Untitled Document"
    
    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """
        Main extraction method that processes a PDF and returns structured outline.
        Optimized for performance to meet the 10-second constraint.
        """
        try:
            doc = fitz.open(pdf_path)
            logger.info(f"Processing PDF: {pdf_path} ({len(doc)} pages)")
            
            # Extract title (only check first 3 pages for performance)
            title = self.extract_title(doc)
            
            # Performance optimization: Process pages in chunks
            CHUNK_SIZE = 5  # Process 5 pages at a time
            all_elements = []
            
            for start_page in range(0, len(doc), CHUNK_SIZE):
                # Process a chunk of pages
                end_page = min(start_page + CHUNK_SIZE, len(doc))
                chunk_elements = []
                
                for page_num in range(start_page, end_page):
                    page = doc[page_num]
                    elements = self.extract_text_with_formatting(page)
                    chunk_elements.extend(elements)
                
                # Merge broken headings within the chunk
                chunk_elements = self.merge_broken_headings(chunk_elements)
                all_elements.extend(chunk_elements)
                
                # Early stopping if we've found enough headings
                # Most documents have 10-20 major headings
                heading_candidates = [elem for elem in chunk_elements 
                                   if any(re.match(pattern, elem["text"].lower()) 
                                        for pattern in self.common_heading_patterns)]
                if len(heading_candidates) > 30:  # We have enough potential headings
                    break
            
            if not all_elements:
                return {"title": title, "outline": []}
            
            # Analyze font patterns efficiently using exact HTML heading standards
            font_analysis = self.analyze_font_structure(all_elements)
            
            # Find most common fonts (likely body text) - use Counter for efficiency
            from collections import Counter
            font_counter = Counter(elem["font"] for elem in all_elements)
            total_elements = len(all_elements)
            common_fonts = {font for font, count in font_counter.items() 
                          if count > total_elements * 0.1}
            
            # Identify headings using multi-factor analysis
            headings = []
            heading_font_sizes = set()  # Use set for faster lookups
            
            for elem in all_elements:
                if self.is_likely_heading(elem, font_analysis, common_fonts):
                    headings.append(elem)
                    heading_font_sizes.add(elem["size"])
            
            # Convert to list for sorting
            heading_font_sizes = sorted(heading_font_sizes, reverse=True)
            
            # Classify heading levels
            outline = []
            for heading in headings:
                level = self.classify_heading_level(heading, font_analysis)
                outline.append({
                    "level": level,
                    "text": heading["text"],
                    "page": heading["page"]
                })
            
            # Sort by page number for consistent output
            outline.sort(key=lambda x: x["page"])
            
            doc.close()
            
            return {
                "title": title,
                "outline": outline
            }
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            return {"title": "Error Processing Document", "outline": []}

def process_pdfs():
    """
    Smart Document Processing Pipeline
    
    This is the main orchestration function that:
    1. Discovers all PDF documents in the input directory
    2. Applies human-like document understanding to each one
    3. Generates structured JSON output representing the document's logical structure
    4. Handles errors gracefully (real-world documents can be messy!)
    
    Each PDF becomes a structured understanding that other systems can use for:
    - Smart search and retrieval
    - Automatic table of contents generation  
    - Content recommendation
    - Document summarization
    """
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the PDF processor
    extractor = PDFOutlineExtractor()
    
    # Find all PDF files in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        try:
            # Generate output filename: filename.pdf -> filename.json
            output_file = output_dir / f"{pdf_file.stem}.json"
            
            logger.info(f"Processing: {pdf_file.name}")
            
            # Extract structured outline
            result = extractor.extract_outline(str(pdf_file))
            
            # Save JSON output with proper formatting
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Generated: {output_file.name}")
            logger.info(f"Title: {result['title']}")
            logger.info(f"Headings found: {len(result['outline'])}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {str(e)}")
            # Create error output file for failed processing
            error_output = output_dir / f"{pdf_file.stem}.json"
            error_result = {
                "title": "Processing Error",
                "outline": [],
                "error": str(e)
            }
            with open(error_output, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2, ensure_ascii=False)

def main():
    """Main entry point for the Smart PDF Document Analyzer."""
    logger.info("🧠 Smart PDF Document Analyzer - Adobe Hackathon 2025")
    logger.info("🔍 Starting intelligent document structure analysis...")
    logger.info("📄 Teaching computers to understand documents like humans do")
    
    try:
        process_pdfs()
        logger.info("✅ Document intelligence analysis completed successfully!")
        logger.info("💡 Ready to power smart document experiences!")
    except Exception as e:
        logger.error(f"Critical error in PDF processing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 