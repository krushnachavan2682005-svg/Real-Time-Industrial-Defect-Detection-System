import uuid
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from src.api.schemas import InspectionResponse
from src.api.services.inspection_service import process_inspection
from src.api.dependencies import get_config
from src.auth.dependencies import require_roles
from src.auth.models import Role

router = APIRouter(tags=["Inspection"])


@router.post(
    "/inspect", 
    response_model=InspectionResponse,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.ENGINEER, Role.OPERATOR))]
)
def inspect_image(file: UploadFile = File(...)):
    """
    Upload an image for industrial defect detection.
    """
    config = get_config()
    api_config = config.get("api", {})
    limits = api_config.get("limits", {})

    # Validation: File extension
    allowed_extensions = limits.get("allowed_extensions", [".jpg", ".jpeg", ".png"])
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    if ext not in allowed_extensions:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {ext}")

    # File size validation could be done via middleware or reading but FastAPI
    # doesn't easily expose content-length directly without reading it all or SpooledTemporaryFile
    # For now, rely on standard limits or if required, add specific check.

    inspection_id = str(uuid.uuid4())[:8]

    response = process_inspection(file, inspection_id)
    return response
