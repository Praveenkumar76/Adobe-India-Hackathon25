from .processor_ultra_minimal import DocumentProcessor
from .models import (
    InputConfig, ProcessingResult, Persona, JobToBeDone,
    ExtractedSection, SubsectionAnalysis, OutputMetadata
)

__version__ = "1.0.0-ultra-fast"
__all__ = [
    "DocumentProcessor", "InputConfig", "ProcessingResult",
    "Persona", "JobToBeDone", "ExtractedSection",
    "SubsectionAnalysis", "OutputMetadata"
] 