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

    return HealthResponse(
        status="healthy", model_loaded=model_loaded, plc_mode=plc_mode
    )
