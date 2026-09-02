import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import io
import cv2
import numpy as np

from src.api.app import create_app
from src.api.dependencies import app_state

app = create_app()


@pytest.fixture
def client():
    # Mocking lifespan
    app_state.inference_engine = "mock_model"
    app_state.plc_service = None
    
    # Bypass auth
    from src.auth.dependencies import get_current_user
    from src.auth.models import AuthenticatedUser, Role
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=1, username="testadmin", role=Role.ADMIN, is_active=True)
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["plc_mode"] == "disabled"


@patch("src.api.routers.inspection.process_inspection")
def test_inspect_valid_image(mock_process, client):
    # Mock the response from process_inspection
    from src.api.schemas import InspectionResponse, InspectionSummary, PLCDispatchInfo

    mock_process.return_value = InspectionResponse(
        inspection_id="test1234",
        decision="PASS",
        severity="NONE",
        summary=InspectionSummary(total_defects=0, affected_classes=[]),
        defects=[],
        latency_ms=10.0,
        plc=PLCDispatchInfo(enabled=False, dispatched=False),
    )

    # Create dummy image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", img)
    file_bytes = buffer.tobytes()

    response = client.post(
        "/api/v1/inspect",
        files={"file": ("test.jpg", io.BytesIO(file_bytes), "image/jpeg")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["inspection_id"] == "test1234"
    assert data["decision"] == "PASS"


def test_inspect_invalid_extension(client):
    response = client.post(
        "/api/v1/inspect",
        files={"file": ("test.txt", io.BytesIO(b"hello world"), "text/plain")},
    )
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]
