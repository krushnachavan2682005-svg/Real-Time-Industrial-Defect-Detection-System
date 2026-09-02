from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from src.api.schemas import DefectSchema, PLCDispatchInfo, InspectionSummary

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
