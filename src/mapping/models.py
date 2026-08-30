from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel

from src.decision.models import DecisionResult


class SpatialRegion(str, Enum):
    TOP_LEFT = "TOP_LEFT"
    TOP_CENTER = "TOP_CENTER"
    TOP_RIGHT = "TOP_RIGHT"
    CENTER_LEFT = "CENTER_LEFT"
    CENTER = "CENTER"
    CENTER_RIGHT = "CENTER_RIGHT"
    BOTTOM_LEFT = "BOTTOM_LEFT"
    BOTTOM_CENTER = "BOTTOM_CENTER"
    BOTTOM_RIGHT = "BOTTOM_RIGHT"
    UNKNOWN = "UNKNOWN"


class MappedDefect(BaseModel):
    # Use dict for detection to avoid pydantic issues with arbitrary objects
    detection: dict
    center_x: float
    center_y: float
    normalized_center_x: float
    normalized_center_y: float
    width: float
    height: float
    area: float
    area_ratio: float
    spatial_region: SpatialRegion

    model_config = {"arbitrary_types_allowed": True}


class FrameMetadata(BaseModel):
    width: int
    height: int
    source_id: str
    timestamp: datetime


class InspectionSummary(BaseModel):
    total_defects: int
    affected_regions: List[str]


class InspectionResult(BaseModel):
    frame: FrameMetadata
    defects: List[MappedDefect]
    decision: DecisionResult
    summary: InspectionSummary
