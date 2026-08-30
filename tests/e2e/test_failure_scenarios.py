import pytest
import io
import cv2
import numpy as np
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.app import create_app
from src.core.exceptions import ConfigurationError

@pytest.fixture(scope="module")
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c

@pytest.fixture
def valid_image_bytes():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    is_success, buffer = cv2.imencode(".jpg", img)
    if is_success:
        return io.BytesIO(buffer).read()
    return b""

def test_missing_model_handled_gracefully(client, valid_image_bytes):
    # Mock ONNX Inference to raise an exception simulating a missing model
    with patch("src.api.dependencies.app_state.inference_engine.predict") as mock_predict:
        mock_predict.side_effect = RuntimeError("ONNX Model not found")
        
        response = client.post(
            "/api/v1/inspect",
            files={"file": ("test_image.jpg", valid_image_bytes, "image/jpeg")},
        )
        # Should be an ApplicationError mapped to a 500 response
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] in ["INTERNAL_ERROR", "ApplicationError"]

def test_plc_failure_handled_safely(client, valid_image_bytes):
    from src.api.dependencies import app_state
    if app_state.plc_service is None:
        pytest.skip("PLC Service is not enabled")
    # Mock PLC Service to simulate connection failure
    with patch.object(app_state.plc_service, "dispatch") as mock_dispatch:
        mock_dispatch.side_effect = Exception("PLC Connection Timeout")
        
        response = client.post(
            "/api/v1/inspect",
            files={"file": ("test_image.jpg", valid_image_bytes, "image/jpeg")},
        )
        # The inspection should still succeed, but PLC dispatch fails safely
        assert response.status_code == 200
        data = response.json()
        assert data["plc"]["status"] == "failed"
        assert "PLC Connection Timeout" in data["plc"]["message"]

def test_invalid_decision_configuration():
    # Attempt to initialize DecisionEngine with invalid config
    from src.decision.decision_engine import DecisionEngine
    with patch("yaml.safe_load") as mock_yaml:
        mock_yaml.return_value = {"invalid": "config"}
        
        with pytest.raises(Exception):
            # Expecting ConfigurationError or generic exception depending on implementation
            DecisionEngine("configs/decision/invalid.yaml")
