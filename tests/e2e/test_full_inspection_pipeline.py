import pytest
import os
import io
import cv2
import numpy as np
from fastapi.testclient import TestClient

from src.api.app import create_app

@pytest.fixture(scope="module")
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c

@pytest.fixture
def valid_image_bytes():
    # Create a dummy image
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Add a white square which might look like something
    cv2.rectangle(img, (50, 50), (150, 150), (255, 255, 255), -1)
    
    is_success, buffer = cv2.imencode(".jpg", img)
    if is_success:
        return io.BytesIO(buffer).read()
    return b""

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "model_loaded" in data
    assert "plc_mode" in data

def test_full_inspection_pipeline(client, valid_image_bytes):
    response = client.post(
        "/api/v1/inspect",
        files={"file": ("test_image.jpg", valid_image_bytes, "image/jpeg")},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate API Layer
    assert "inspection_id" in data
    assert "decision" in data
    assert "severity" in data
    assert "summary" in data
    assert "defects" in data
    assert "latency_ms" in data
    assert "plc" in data
    
    # Validate Decision Layer
    assert data["decision"] in ["PASS", "REVIEW", "REJECT"]
    assert data["severity"] in ["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    # Validate Mapping Layer
    for defect in data["defects"]:
        assert "class_name" in defect
        assert "confidence" in defect
        assert "bbox" in defect
        assert "region" in defect
        
        bbox = defect["bbox"]
        assert "x1" in bbox
        assert "y1" in bbox
        assert "x2" in bbox
        assert "y2" in bbox
        
        assert bbox["x1"] <= bbox["x2"]
        assert bbox["y1"] <= bbox["y2"]
        assert 0.0 <= defect["confidence"] <= 1.0

    # Validate Response Contract latency
    assert data["latency_ms"] >= 0.0
