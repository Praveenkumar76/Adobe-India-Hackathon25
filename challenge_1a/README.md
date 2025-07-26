# Smart PDF Document Analyzer - Adobe Hackathon 2025 Challenge 1A

## Overview

This project is a **Smart PDF Document Analyzer** that extracts structured outlines from PDF documents. It intelligently identifies document titles and hierarchical headings (H1, H2, H3) with their page numbers, outputting the results in a clean JSON format.

## Problem Statement

PDFs are ubiquitous but machines don't naturally understand their structure. This solution bridges that gap by teaching computers to understand document structure like humans do, enabling smarter document experiences such as semantic search, recommendation systems, and insight generation.

## Solution Approach

### Core Intelligence Components

1. **Visual Pattern Recognition** - Analyzes typography, font sizes, and formatting
2. **Contextual Understanding** - Considers relationships between text elements
3. **Structural Intelligence** - Recognizes academic and professional document conventions
4. **Multi-Factor Decision Making** - Combines multiple signals for accurate heading detection
5. **Multilingual Support** - Handles English, Japanese, and Hindi documents

### Key Features

- **Heading Splitting Fix**: Merges text elements that are split across lines but belong to the same heading
- **Multilingual Pattern Recognition**: Supports multiple languages including Japanese (第1章) and Hindi (परिचय)
- **Performance Optimization**: Processes documents in chunks with early stopping for efficiency
- **Edge Case Handling**: Supports colored text, underlined text, non-standard numbering (Part A, Section III)
- **Intelligent Classification**: Uses weighted scoring system combining font size, formatting, patterns, and positioning

### Technical Implementation

- **Primary Library**: PyMuPDF (fitz) for PDF text extraction with formatting information
- **Pattern Recognition**: Regular expressions for multilingual heading patterns
- **Font Analysis**: Statistical analysis of font usage to identify body text vs headings
- **Layout Analysis**: Bounding box analysis for position-based heading detection
- **Hierarchy Detection**: Multi-signal approach combining patterns, font sizes, and formatting

## Input/Output Format

### Input
- PDF files (up to 50 pages) placed in `/app/input` directory

### Output
JSON files in `/app/output` directory with the following structure:

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

## Dependencies

- **PyMuPDF (1.23.24)**: Lightweight PDF processing library (~20MB)
- **Python 3.9**: Base runtime
- **Standard Library**: json, os, pathlib, re, collections, logging

**Total Model Size**: < 30MB (well under the 200MB limit)

## Docker Requirements

- **Platform**: linux/amd64 (explicitly specified)
- **CPU Only**: No GPU dependencies
- **Offline**: No network/internet calls
- **Performance**: < 10 seconds for 50-page PDFs

## Build and Run Instructions

### Expected Execution (As per Hackathon Requirements)

1. **Build the Docker image:**
   ```bash
   docker build --platform linux/amd64 -t challenge1a:latest .
   ```
   
2. **Run the solution:**
   ```bash
   docker run --rm -v "${PWD}/sample_dataset/pdfs:/app/input" -v "${PWD}/sample_dataset/outputs:/app/output" --network none challenge1a:latest
   ```

### Directory Structure
```
your-project/
├── input/               # Place your PDF files here
│   ├── document1.pdf
│   └── document2.pdf
├── output/              # JSON outputs will be generated here
│   ├── document1.json
│   └── document2.json
├── Dockerfile
├── process_pdfs.py
├── requirements.txt
└── README.md
```

### Local Development (Optional)

If you want to run locally without Docker:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create input/output directories:**
   ```bash
   mkdir -p input output
   ```

3. **Place PDFs in input/ and run:**
   ```bash
   python process_pdfs.py
   ```

## Performance Characteristics

- **Execution Time**: < 5 seconds for typical 50-page PDFs
- **Memory Usage**: < 100MB peak memory
- **CPU Usage**: Single-threaded, optimized for 8-core systems
- **Accuracy**: High precision/recall for heading detection across document types

## Multilingual Support

The solution supports:

- **English**: Chapter 1, 1.1 Introduction, METHODOLOGY
- **Japanese**: 第1章, 1．1 はじめに, まとめ
- **Hindi**: अध्याय 1, 1. परिचय, निष्कर्ष
- **Universal**: Part A, Section III, Roman numerals

## Architecture Highlights

### Heading Detection Pipeline

1. **Text Extraction**: Extract all text with detailed formatting information
2. **Heading Merging**: Intelligently merge split headings using proximity and formatting analysis
3. **Font Analysis**: Identify common body fonts vs heading fonts
4. **Pattern Matching**: Apply multilingual regex patterns
5. **Scoring System**: Weighted multi-factor scoring for heading classification
6. **Level Classification**: Determine H1/H2/H3 based on patterns and font hierarchy

### Edge Case Handling

- **Split Headings**: "Introduction\nto AI" → "Introduction to AI"
- **Colored/Underlined Text**: Detected via formatting flags
- **Non-standard Numbering**: Part A, Section III, Appendix B
- **Position-based Detection**: Centered text, margin alignment
- **Scanned PDFs**: Graceful degradation (though OCR not implemented due to size constraints)

## Code Quality

- **Modular Design**: Reusable components for future rounds
- **Error Handling**: Graceful failure with error JSON output
- **Logging**: Comprehensive logging for debugging
- **Documentation**: Extensive inline documentation
- **Performance**: Optimized for speed and memory efficiency

## Constraints Compliance

| Constraint | Requirement | Status |
|------------|-------------|---------|
| Execution Time | ≤ 10 seconds for 50-page PDF | ✅ < 5 seconds |
| Model Size | ≤ 200MB | ✅ < 30MB |
| Network | No internet access | ✅ Fully offline |
| Runtime | CPU only (amd64) | ✅ Single-threaded |
| Platform | linux/amd64 | ✅ Explicitly specified |

## Testing

The solution has been tested on:
- Simple academic papers
- Complex multi-column documents
- Multilingual documents
- Documents with various heading styles
- Large documents (40+ pages)

## Future Enhancements

- OCR support for scanned PDFs (if size constraints allow)
- Additional language support
- Table and figure detection
- Cross-reference analysis 