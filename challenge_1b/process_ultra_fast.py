#!/usr/bin/env python3
import json
import time
from pathlib import Path
from smart_doc_intel.processor_ultra_minimal import DocumentProcessor
from smart_doc_intel.models import (
    InputConfig, ProcessingResult, OutputMetadata,
    ExtractedSection, SubsectionAnalysis
)

def process_collection_fast(collection_path: Path) -> ProcessingResult:
    """Fast processing with minimal overhead."""
    print(f"Loading config from {collection_path}...")
    
    with open(collection_path / "challenge1b_input.json") as f:
        data = json.load(f)
    config = InputConfig(**data)
    
    processor = DocumentProcessor()
    start_time = time.time()
    
    all_sections = []
    all_analyses = []
    
    print(f"Processing {len(config.documents)} documents...")
    
    for i, doc in enumerate(config.documents, 1):
        doc_path = collection_path / doc.filename
        print(f"  [{i}/{len(config.documents)}] {doc.filename}...")
        
        if not doc_path.exists():
            # Quick mock data
            section = ExtractedSection(
                document=doc.filename,
                section_title=f"Mock: {doc.title}",
                importance_rank=i,
                page_number=1
            )
            analysis = SubsectionAnalysis(
                document=doc.filename,
                refined_text=f"Mock content for {doc.title}",
                page_number=1,
                parent_section=None,
                relevance_score=0.8,
                key_points=["Mock key point"]
            )
            all_sections.append(section)
            all_analyses.append(analysis)
        else:
            try:
                result = processor.process_document(doc_path, config.persona, config.job_to_be_done)
                
                for idx, section in enumerate(result.sections[:5], 1):  # Limit to 5 sections per doc
                    all_sections.append(ExtractedSection(
                        document=doc.filename,
                        section_title=section['title'][:100],  # Limit title length
                        importance_rank=len(all_sections) + 1,
                        page_number=section['page_number']
                    ))
                    
                    all_analyses.append(SubsectionAnalysis(
                        document=doc.filename,
                        refined_text=section['content'][:400],  # Limit content
                        page_number=section['page_number'],
                        parent_section=section['parent_section'],
                        relevance_score=section['relevance_score'],
                        key_points=section['key_points'][:2]  # Limit key points
                    ))
            except Exception as e:
                print(f"    Error: {e}")
                continue
    
    # Quick sort by relevance
    all_analyses.sort(key=lambda x: x.relevance_score, reverse=True)
    
    # Update ranks quickly
    for i, section in enumerate(all_sections, 1):
        section.importance_rank = i
    
    result = ProcessingResult(
        metadata=OutputMetadata(
            input_documents=[doc.filename for doc in config.documents],
            persona=config.persona.role,
            job_to_be_done=config.job_to_be_done.task,
            total_processing_time=time.time() - start_time
        ),
        extracted_sections=all_sections,
        subsection_analysis=all_analyses
    )
    
    return result

def main():
    """Ultra-fast main processing."""
    collections = [
        ("Collection 1", "Travel Planning"),
        ("Collection 2", "Adobe Acrobat Learning"), 
        ("Collection 3", "Recipe Collection")
    ]
    
    total_start = time.time()
    
    for collection_name, description in collections:
        print(f"\n=== {description} ===")
        collection_path = Path(collection_name)
        
        if not collection_path.exists():
            print(f"Skipping {collection_name} - directory not found")
            continue
            
        try:
            result = process_collection_fast(collection_path)
            
            # Save quickly
            output_path = collection_path / "challenge1b_output.json"
            print(f"Saving to {output_path}...")
            
            with open(output_path, "w") as f:
                json.dump(result.model_dump(), f, indent=2, default=str)
            
            print(f"✓ {description}: {len(result.extracted_sections)} sections in {result.metadata.total_processing_time:.1f}s")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n🎉 Total time: {time.time() - total_start:.1f}s")

if __name__ == "__main__":
    main() 