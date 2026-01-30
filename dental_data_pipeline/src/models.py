
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional
from enum import Enum

class ReconstructionType(str, Enum):
    CROWN = "AnatomicWaxup"
    PONTIC = "WaxupPontic"
    IMPLANT = "Implant" # Placeholder string, to be verified
    VENEER = "Veneer"   # Placeholder string, to be verified
    ANTAGONIST = "Antagonist"
    OTHER = "Other"
    
    @classmethod
    def _missing_(cls, value):
        return cls.OTHER

class Tooth(BaseModel):
    number: int
    reconstruction_type: ReconstructionType
    margin_points: List[Tuple[float, float, float]] = Field(default_factory=list)

    @property
    def is_valid_training_sample(self) -> bool:
        """Returns True if it's a Crown and has >50 margin points."""
        return self.reconstruction_type == ReconstructionType.CROWN and len(self.margin_points) > 50

class Case(BaseModel):
    id: str
    jaw_type: str = "Unknown"
    teeth: List[Tooth] = Field(default_factory=list)
    missing_files: List[str] = Field(default_factory=list) # e.g. ["constructionInfo", "scan_stl"]
    scan_vertex_count: int = 0
    file_size_mb: float = 0.0
