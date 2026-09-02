from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List, Any, Dict
from src.persistence.schemas import PaginatedResponse, InspectionHistoryItem
from src.persistence.repositories.inspection_repository import InspectionRepository
from src.api.dependencies import get_inspection_repository

router = APIRouter(tags=["History"])

@router.get("/inspections", response_model=PaginatedResponse)
def list_inspections(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    decision: Optional[str] = Query(None, description="Filter by decision (PASS/REVIEW/REJECT)"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    defect_class: Optional[str] = Query(None, description="Filter by defect class"),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    repo: InspectionRepository = Depends(get_inspection_repository)
):
    if repo is None:
        raise HTTPException(status_code=503, detail="Persistence layer is not configured")
        
    filters = {}
    if decision:
        filters["decision"] = decision
    if severity:
        filters["severity"] = severity
    if defect_class:
        filters["defect_class"] = defect_class
    if start_time:
        filters["start_time"] = start_time
    if end_time:
        filters["end_time"] = end_time

    items, total = repo.list(page=page, page_size=page_size, filters=filters)
    
    return PaginatedResponse(
        items=[item.model_dump() for item in items],
        page=page,
        page_size=page_size,
        total=total
    )

@router.get("/inspections/{inspection_id}", response_model=InspectionHistoryItem)
def get_inspection(inspection_id: str, repo: InspectionRepository = Depends(get_inspection_repository)):
    if repo is None:
        raise HTTPException(status_code=503, detail="Persistence layer is not configured")
        
    item = repo.get_by_id(inspection_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    return item
