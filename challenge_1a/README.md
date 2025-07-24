# Smart PDF Document Analyzer

## What You're Building

You're building a **Smart PDF Document Analyzer** - a system that can "read" any PDF document and understand its structure like a human would, then output that understanding in a machine-readable format.

## The Real-World Problem

Imagine you have thousands of research papers, reports, or books in PDF format. Right now, computers see them as just a bunch of text and images. Your job is to teach the computer to understand:
- "This is the main title"
- "This is a major section heading" 
- "This is a sub-section under that major heading"
- "This part appears on page 5"

## Exactly What Your System Must Do

### Input:
- One or more PDF files (up to 50 pages each)
- Could be simple documents (like a basic report) or complex ones (academic papers with multiple columns, tables, images)

### Processing:
Your system must analyze each PDF and identify:
1. **Document Title** - The main title of the document
2. **Heading Hierarchy** - Organize headings into levels:
   - **H1** = Major sections (like "Introduction", "Methodology") 
   - **H2** = Sub-sections (like "Data Collection" under "Methodology")
   - **H3** = Sub-sub-sections (like "Survey Design" under "Data Collection")
3. **Location Tracking** - Which page number each heading appears on

### Output:
For each PDF file, create a JSON file with this exact structure:
```json
{
  "title": "Understanding Artificial Intelligence in Healthcare",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "Current Healthcare Challenges",
      "page": 2
    },
    {
      "level": "H3",
      "text": "Data Privacy Concerns", 
      "page": 3
    }
  ]
}
```

## The Technical Challenge

### Why This Is Hard:
1. **PDFs are messy** - Unlike web pages with HTML tags, PDFs don't have built-in structure
2. **Inconsistent formatting** - Different documents use different fonts, sizes, styles for headings
3. **Visual complexity** - Some PDFs have multiple columns, images, tables that can confuse text extraction
4. **No universal rules** - You can't just say "bigger font = main heading" because many PDFs break this rule

### Our Solution Approach:
We've built intelligence that can:
- **Extract all text from PDFs** with formatting details
- **Analyze formatting patterns** (font size, weight, positioning) like a human would
- **Recognize heading patterns and hierarchy** using multiple clues
- **Handle edge cases and inconsistencies** gracefully
- **Work fast and efficiently** to meet performance demands

## How Our Smart Analyzer Works

### 1. Human-Like Document Understanding
Just like how you'd scan a document and immediately recognize "this looks like a title" or "this seems like a section heading", our system:

- **Visual Pattern Recognition**: Analyzes font size, weight, and styling
- **Contextual Understanding**: Considers position, spacing, and relationship to other text
- **Structural Intelligence**: Recognizes numbering patterns (1., 1.1, 1.1.1) and academic conventions
- **Multi-Factor Decision Making**: Combines multiple signals rather than relying on single rules

### 2. Sophisticated Heading Detection
Our system doesn't just look at font size. It considers:
- **Typography Patterns**: Bold text, font family changes, size variations
- **Academic Conventions**: Chapter numbering, section patterns, title case usage
- **Document Structure**: How text elements relate to each other spatially
- **Content Analysis**: Length, complexity, and semantic clues

### 3. Intelligent Title Extraction
The system identifies document titles by:
- **Metadata Analysis**: Checking PDF properties first
- **Visual Prominence**: Finding the largest, most prominent text on the first page
- **Position Intelligence**: Considering typical title placement patterns
- **Content Validation**: Ensuring the extracted title makes semantic sense

### 4. Multilingual Intelligence
Supports global documents through:
- **Unicode Compatibility**: Full international character support
- **Pattern Flexibility**: Works across different writing systems
- **Cultural Adaptability**: Recognizes different document conventions

## Libraries Used

- **PyMuPDF (fitz) 1.23.24**: Primary PDF processing library
  - Chosen for its excellent text extraction capabilities with formatting details
  - Provides font, size, style, and positioning information
  - Lightweight and fast processing
  - No GPU dependencies
  - Well under 200MB model size constraint

## Performance Optimizations

- Efficient text extraction using PyMuPDF's dictionary format
- Single-pass document processing
- Optimized font pattern analysis
- Memory-efficient processing for large documents

## Constraints and Requirements

### Performance Demands:
- ✅ **Speed**: Process a 50-page PDF in under 10 seconds
- ✅ **Memory**: Use less than 16GB RAM  
- ✅ **Size**: If using ML models, keep them under 200MB
- ✅ **Offline**: No internet access during processing

### Technical Stack:
- ✅ **Language**: Python (recommended) or any language that works in Docker
- ✅ **Container**: Must run in Docker on AMD64/Linux systems
- ✅ **Dependencies**: Only open-source libraries allowed

### Deployment Requirements:
Your solution will be tested like this:
1. Put PDF files in an input folder
2. Run your Docker container  
3. Check output folder for corresponding JSON files
4. Validate JSON format and accuracy

## Success Criteria

### What Gets You Points:
1. **Accuracy (25 points)**: How well you detect headings and their correct hierarchy levels
2. **Performance (10 points)**: Speed and resource efficiency 
3. **Bonus (10 points)**: Handle non-English documents (like Japanese)

### What You'll Be Judged On:
- ✅ Does your system correctly identify the document title?
- ✅ Does it properly classify H1, H2, H3 headings?
- ✅ Does it work on both simple and complex PDF layouts?
- ✅ Does it run within the time and resource limits?
- ✅ Is your code well-documented and the Docker container reliable?

## The Bigger Picture

This isn't just about extracting text - you're building the foundation for smarter document systems. Your outline extractor could power:
- **Document search engines** that understand context
- **Automatic table-of-contents** generation  
- **Content recommendation systems**
- **Document summarization tools**

Think of yourself as building the "document understanding brain" that other applications will rely on.

## Build and Run Commands

### Build Command
```bash
docker build --platform linux/amd64 -t smart-pdf-analyzer .
```

### Run Command  
```bash
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none smart-pdf-analyzer
```

## Output Format

The solution generates JSON files with the following structure:
```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

## Design Decisions

1. **No Internet Dependencies**: Solution works completely offline
2. **CPU-Only Processing**: No GPU requirements for maximum compatibility
3. **Modular Design**: Clean separation of concerns for easy extension
4. **Robust Error Handling**: Graceful handling of malformed PDFs
5. **Unicode Support**: Full multilingual document support
6. **Performance Focus**: Optimized for the 10-second constraint on 50-page documents

## Sample Solution Structure
```
Challenge_1a/
├── sample_dataset/
│   ├── outputs/         # JSON files provided as outputs
│   ├── pdfs/            # Input PDF files
│   └── schema/          # Output schema definition
│       └── output_schema.json
├── Dockerfile           # Docker container configuration
├── process_pdfs.py      # Main processing script
└── README.md           # This file
```

## Testing Your Solution

### Local Testing
```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-processor .

# Test with sample data
docker run --rm -v $(pwd)/sample_dataset/pdfs:/app/input:ro -v $(pwd)/sample_dataset/outputs:/app/output --network none pdf-processor
```

### Validation Checklist
- ✅ All PDFs in input directory are processed
- ✅ JSON output files are generated for each PDF
- ✅ Output format matches required structure
- ✅ Output conforms to schema in sample_dataset/schema/output_schema.json
- ✅ Processing completes within 10 seconds for 50-page PDFs
- ✅ Solution works without internet access
- ✅ Memory usage stays within 16GB limit
- ✅ Compatible with AMD64 architecture

**Important**: This is a sample implementation. Participants should develop their own solutions that meet all the official challenge requirements and constraints. 