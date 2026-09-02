from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum

class TimeRange(BaseModel):
    start: datetime
    end: datetime

class InspectionStatistics(BaseModel):
    total_inspections: int
    pass_count: int
    review_count: int
    reject_count: int
    pass_rate: float
    review_rate: float
    reject_rate: float
    average_defects_per_inspection: float
    average_latency_ms: float

class DefectAnalytics(BaseModel):
    class_name: str
    total_occurrences: int
    percentage: float

class TrendPoint(BaseModel):
    timestamp: datetime
    total_inspections: int
    pass_count: int
    review_count: int
    reject_count: int
    reject_rate: float

class QualityAlert(BaseModel):
    severity: str
    message: str
    metric: str
    threshold: float
    actual_value: float

class AnalyticsSummary(BaseModel):
    time_range: TimeRange
    inspection_statistics: InspectionStatistics
    defect_distribution: List[DefectAnalytics]
    trends: List[TrendPoint]
    quality_alerts: List[QualityAlert]

    model_config = ConfigDict(from_attributes=True)
