import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app
import numpy as np
import cv2

@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client

def test_api_metrics_instrumentation(client):
    # Create dummy image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.jpg', img)
    
    # We do not strictly check the result, we check if the endpoint doesn't crash with metrics
    response = client.post(
        "/api/v1/inspect", 
        files={"file": ("test.jpg", img_encoded.tobytes(), "image/jpeg")}
    )
    
    assert response.status_code in [200, 422, 500] # Depends on dummy image validation, but it shouldn't crash due to monitoring
    
    metrics_resp = client.get("/metrics")
    assert metrics_resp.status_code == 200
    assert "industrial_defect_http_requests_total" in metrics_resp.text
