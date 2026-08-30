from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.decision.models import DecisionResult


class MappedDefect(BaseModel):
    """A defect detection mapped to spatial coordinates and regions."""

    # Original detection fields stored as dict for serialization, or could just embed Detection
    # Since Detection is a dataclass, we can use a dict or nested model.
    # We will use flat fields or a dict for simplicity, but let's use flat fields from Detection
    # to avoid complex Pydantic dataclass integration if not needed, or just dict.
    # Actually, we can just define original_detection as dict.
    original_detection: dict

    center_x: int
    center_y: int
    normalized_center_x: float
    normalized_center_y: float
    width: int
    height: int
    area: int
    area_ratio: float
    spatial_region: str


class FrameMetadata(BaseModel):
    """Metadata about the processed frame."""

    width: int
    height: int
    source_id: str
    timestamp: datetime


class InspectionResult(BaseModel):
    """The final structured inspection result containing metadata, mapped defects, and decision."""

    frame: FrameMetadata
    defects: List[MappedDefect]
    decision: DecisionResult
    defect_count: int
    timestamp: datetime
