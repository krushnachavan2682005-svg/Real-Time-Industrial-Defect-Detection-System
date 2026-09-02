from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.api.schemas import DefectSchema, InspectionSummary, PLCDispatchInfo


class PaginatedResponse(BaseModel):
    items: List[dict]
    page: int
    page_size: int
    total: int


class InspectionHistoryItem(BaseModel):
    inspection_id: str
    decision: str
    severity: str
    summary: InspectionSummary
    defects: List[DefectSchema]
    latency_ms: float
    plc: PLCDispatchInfo
    timestamp: datetime
