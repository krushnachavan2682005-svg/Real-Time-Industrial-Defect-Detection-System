from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
from src.analytics.models import AnalyticsSummary, DefectAnalytics, TrendPoint
from src.analytics.service import AnalyticsService
from src.analytics.config import load_analytics_config, AnalyticsSettings
from src.persistence.repositories.inspection_repository import InspectionRepository
from src.api.dependencies import get_inspection_repository
from src.core.exceptions import ApplicationError

router = APIRouter(tags=["Analytics"])

def get_analytics_service(repo: InspectionRepository = Depends(get_inspection_repository)) -> AnalyticsService:
    if repo is None:
        raise HTTPException(status_code=503, detail="Persistence layer is not configured")
    config = load_analytics_config()
    return AnalyticsService(repository=repo, config=config)

def parse_time(t: str) -> Optional[datetime]:
    if not t:
        return None
    try:
        return datetime.fromisoformat(t)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use ISO 8601.")

@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        return service.get_summary(parse_time(start_time), parse_time(end_time))
    except ApplicationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/defects", response_model=List[DefectAnalytics])
def get_defect_analytics(
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        return service.get_defect_distribution(parse_time(start_time), parse_time(end_time))
    except ApplicationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trends", response_model=List[TrendPoint])
def get_trend_analytics(
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    interval: str = Query("day", description="Aggregation interval (hour, day, week)"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        return service.get_trends(interval, parse_time(start_time), parse_time(end_time))
    except ApplicationError as e:
        raise HTTPException(status_code=400, detail=str(e))
