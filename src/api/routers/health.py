from fastapi import APIRouter
from src.api.schemas import HealthResponse
from src.api.dependencies import app_state

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health():
    """Returns the health status of the API and its components."""
    model_loaded = app_state.inference_engine is not None
    plc_mode = "disabled"
    if app_state.plc_service is not None:
        plc_mode = "simulation"  # based on current initialization
        
    db_status = "disabled"
    if app_state.inspection_repository is not None:
        db_healthy = app_state.inspection_repository.health_check()
        db_status = "healthy" if db_healthy else "unhealthy"

    return {
        "status": "healthy" if db_status in ["healthy", "disabled"] else "unhealthy",
        "model_loaded": model_loaded,
        "plc_mode": plc_mode,
        "database": db_status
    }

