# Smart PDF Document Analyzer & Multi-Collection Analysis System

## Overview
This project combines two powerful PDF processing capabilities:

**Smart Document Structure Analyzer** - Extracts hierarchical document structure from PDFs

**Multi-Collection Content Analyzer** - Processes document collections based on specific personas and use cases

## Key Features

### Document Structure Analysis
- Extracts title and heading hierarchy (H1-H3) from PDFs
- Tracks page locations of all structural elements
- Handles complex layouts (multi-column, images, tables)
- Works with multilingual documents

### Multi-Collection Analysis
- Persona-based content extraction (travel, HR, culinary, etc.)
- Importance ranking of extracted content
- Cross-document synthesis
- Standardized JSON output format

## Project Structure
```
Challenge_1/
├── Collection_1/                    # Example: Travel Planning
│   ├── PDFs/                       # Document collection
│   ├── input.json                  # Configuration
│   └── output.json                 # Analysis results
├── sample_dataset/
│   ├── outputs/                    # Sample outputs
│   └── pdfs/                      # Sample PDFs
├── smart_doc_intel/                # Core processing engine
│   ├── models.py                   # Data models
│   ├── processor.py                # Processing logic
│   └── analyzer.py                 # Analysis components
├── Dockerfile                      # Container configuration
├── Dockerfile.fast                 # Optimized build
├── process_pdfs.py                 # Main PDF processor
├── process_collections.py          # Collection processor
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Technical Specifications

### Requirements
- Python 3.8+
- Docker (for containerized deployment)
- CPU-only operation (no GPU required)
- Offline processing capability

### Performance
- Processes 50-page PDFs in <10 seconds
- Memory usage <16GB
- Model size <200MB
- Supports batch processing of document collections

## Usage

All operations are performed using Docker containers - no local Python installation required.

## Docker Deployment

### Build Image
```bash
docker build --platform linux/amd64 -t pdf-analyzer .
```

### Run Container
```bash
# Document structure analysis
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-analyzer

# Collection analysis (fast version)
docker build -f Dockerfile.fast -t challenge1b-fast .
docker run --rm -v "${PWD}:/workspace" challenge1b-fast
```

## Input/Output Formats

### Document Structure Output
```json
{
  "title": "Document Title",
  "outline": [
    {"level": "H1", "text": "Introduction", "page": 1},
    {"level": "H2", "text": "Background", "page": 2}
  ]
}
```

### Collection Analysis Output
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf"],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a 4-day trip"
  },
  "extracted_sections": [
    {
      "document": "guide.pdf",
      "section_title": "Best Hotels",
      "importance_rank": 1,
      "page_number": 5
    }
  ]
}
```

## Supported Use Cases
- **Academic Research** - Extract structured content from research papers
- **Business Intelligence** - Analyze collections of reports
- **Learning Systems** - Process educational materials
- **Content Management** - Organize document repositories

## Design Highlights
- **Modular Architecture**: Separate components for PDF processing and content analysis
- **Persona Adaptation**: Custom processing based on user roles
- **Performance Optimized**: Efficient memory and CPU usage
- **Robust Error Handling**: Graceful degradation with malformed inputs

## Testing
```bash
# Run unit tests
python -m unittest discover

# Validate against sample data
python validate_outputs.py sample_dataset/outputs/
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.
