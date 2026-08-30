from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class Severity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Decision(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


class DefectSummary(BaseModel):
    total_defects: int
    detections_by_class: Dict[str, int]
    affected_classes: List[str]
    maximum_confidence: float
    dominant_class: Optional[str]


class DecisionResult(BaseModel):
    decision: Decision
    severity: Severity
    reason: str
    total_defects: int
    affected_classes: List[str]
    highest_confidence: float
    timestamp: datetime
