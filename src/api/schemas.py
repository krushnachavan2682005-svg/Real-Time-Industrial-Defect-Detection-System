from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="API health status (e.g., healthy)")
    model_loaded: bool = Field(..., description="Whether the ONNX model is loaded")
    plc_mode: str = Field(
        ..., description="Current PLC mode (e.g., simulation, connected)"
    )
    database: Optional[str] = Field(
        None, description="Database status (e.g., healthy, disabled, unhealthy)"
    )


class BBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class DefectSchema(BaseModel):
    class_name: str
    confidence: float
    bbox: BBox
    region: str


class InspectionSummary(BaseModel):
    total_defects: int
    affected_classes: List[str]


class PLCDispatchInfo(BaseModel):
    enabled: bool
    dispatched: bool
    status: Optional[str] = None
    message: Optional[str] = None


class InspectionResponse(BaseModel):
    inspection_id: str
    decision: str
    severity: str
    summary: InspectionSummary
    defects: List[DefectSchema]
    latency_ms: float
    plc: PLCDispatchInfo


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
