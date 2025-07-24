from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

class ChallengeInfo(BaseModel):
    challenge_id: str
    test_case_name: str

class Document(BaseModel):
    filename: str
    title: str

class Persona(BaseModel):
    role: str
    expertise: str
    background: str

class JobToBeDone(BaseModel):
    task: str
    objectives: Optional[List[str]] = Field(default_factory=list)

class InputConfig(BaseModel):
    challenge_info: ChallengeInfo
    documents: List[Document]
    persona: Persona
    job_to_be_done: JobToBeDone

class ExtractedSection(BaseModel):
    document: str
    section_title: str
    importance_rank: int
    page_number: int

class SubsectionAnalysis(BaseModel):
    document: str
    refined_text: str
    page_number: int
    parent_section: Optional[str] = None
    relevance_score: float = Field(ge=0, le=1)
    key_points: List[str] = Field(default_factory=list)

class OutputMetadata(BaseModel):
    input_documents: List[str]
    persona: str
    job_to_be_done: str
    processing_timestamp: datetime = Field(default_factory=datetime.now)
    total_processing_time: float

class ProcessingResult(BaseModel):
    metadata: OutputMetadata
    extracted_sections: List[ExtractedSection]
    subsection_analysis: List[SubsectionAnalysis]

    class Config:
        arbitrary_types_allowed = True 