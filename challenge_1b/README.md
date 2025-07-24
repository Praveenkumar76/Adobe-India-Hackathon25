# Challenge 1b: Multi-Collection PDF Analysis

## Overview
Advanced PDF analysis solution that processes multiple document collections and extracts relevant content based on specific personas and use cases.

## Project Structure
```
Challenge_1b/
├── Collection 1/                    # Travel Planning
│   ├── PDFs/                       # South of France guides
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── Collection 2/                    # Adobe Acrobat Learning
│   ├── PDFs/                       # Acrobat tutorials
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── Collection 3/                    # Recipe Collection
│   ├── PDFs/                       # Cooking guides
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── smart_doc_intel/                 # Core processing engine
├── process_collections.py           # Main processing script
├── requirements.txt                 # Dependencies
└── README.md
```

## Collections

### Collection 1: Travel Planning
- **Challenge ID**: round_1b_002
- **Persona**: Travel Planner
- **Task**: Plan a 4-day trip for 10 college friends to South of France
- **Documents**: 7 travel guides

### Collection 2: Adobe Acrobat Learning
- **Challenge ID**: round_1b_003
- **Persona**: HR Professional
- **Task**: Create and manage fillable forms for onboarding and compliance
- **Documents**: 15 Acrobat guides

### Collection 3: Recipe Collection
- **Challenge ID**: round_1b_001
- **Persona**: Food Contractor
- **Task**: Prepare vegetarian buffet-style dinner menu for corporate gathering
- **Documents**: 9 cooking guides

## Input/Output Format

### Input JSON Structure
```json
{
  "challenge_info": {
    "challenge_id": "round_1b_XXX",
    "test_case_name": "specific_test_case"
  },
  "documents": [{"filename": "doc.pdf", "title": "Title"}],
  "persona": {"role": "User Persona"},
  "job_to_be_done": {"task": "Use case description"}
}
```

### Output JSON Structure
```json
{
  "metadata": {
    "input_documents": ["list"],
    "persona": "User Persona",
    "job_to_be_done": "Task description"
  },
  "extracted_sections": [
    {
      "document": "source.pdf",
      "section_title": "Title",
      "importance_rank": 1,
      "page_number": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "source.pdf",
      "refined_text": "Content",
      "page_number": 1
    }
  ]
}
```
## Run
```
docker build -f Dockerfile.fast -t challenge1b-fast .
docker run --rm -v "${PWD}:/workspace" challenge1b-fast
```

## Usage

All operations are performed using Docker containers - no local Python installation required.

## Key Features

- **Persona-based content analysis**: Understands user role and expertise
- **Importance ranking**: Ranks extracted sections by relevance
- **Multi-collection processing**: Handles different document types and use cases
- **Structured JSON output**: Standardized format with metadata
- **CPU-only operation**: No GPU required
- **Offline processing**: No internet connection needed during execution

## Technical Constraints

- **CPU only** (no GPU required)
- **Model size** ≤ 1GB
- **Processing time** ≤ 60 seconds for 3-5 documents
- **Offline operation** (no internet access during execution)

## Architecture

The system consists of:

1. **Document Processor**: Handles PDF extraction and structure analysis
2. **Persona Analyzer**: Understands user context and requirements  
3. **Content Ranker**: Scores and prioritizes content based on relevance
4. **Multi-document Analyzer**: Synthesizes information across documents

## Performance

- Processing time: < 60 seconds for 3-5 documents
- Model size: < 1GB total
- Memory efficient: Processes documents individually
- Relevance scoring: Semantic similarity using transformer embeddings

Note: This README provides a brief overview of the Challenge 1b solution structure based on available sample data. 