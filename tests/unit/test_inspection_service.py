import pytest
from unittest.mock import MagicMock, patch
import numpy as np
import cv2

from src.api.services.inspection_service import process_inspection, InvalidImageError
from src.vision.detection import Detection
from src.decision.models import DecisionResult, Decision, Severity
from src.mapping.models import InspectionResult, FrameMetadata
from datetime import datetime


class MockUploadFile:
    def __init__(self, content):
        self.file = MagicMock()
        self.file.read.return_value = content
        self.filename = "test.jpg"


@pytest.fixture
def valid_image_bytes():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", img)
    return buffer.tobytes()


@patch("src.api.services.inspection_service.get_plc_service")
@patch("src.api.services.inspection_service.get_result_builder")
@patch("src.api.services.inspection_service.get_decision_engine")
@patch("src.api.services.inspection_service.get_postprocessor")
@patch("src.api.services.inspection_service.get_inference_engine")
@patch("src.api.services.inspection_service.get_config")
def test_process_inspection_success(
    mock_get_config,
    mock_get_inference,
    mock_get_post,
    mock_get_decision,
    mock_get_result,
    mock_get_plc,
    valid_image_bytes,
):
    # Setup mocks
    mock_get_config.return_value = {"api": {"limits": {}}}

    inference_mock = MagicMock()
    inference_mock.predict.return_value = np.zeros((1, 84, 8400))
    inference_mock.imgsz = (224, 224)
    mock_get_inference.return_value = inference_mock

    post_mock = MagicMock()
    post_mock.process.return_value = [
        Detection(
            class_id=0, class_name="crazing", confidence=0.9, x1=10, y1=10, x2=20, y2=20
        )
    ]
    mock_get_post.return_value = post_mock

    decision_mock = MagicMock()
    decision_mock.evaluate.return_value = DecisionResult(
        decision=Decision.REJECT,
        severity=Severity.HIGH,
        reason="Test",
        total_defects=1,
        affected_classes=["crazing"],
        highest_confidence=0.9,
        timestamp=datetime.now(),
    )
    mock_get_decision.return_value = decision_mock

    result_mock = MagicMock()
    result_mock.build.return_value = InspectionResult(
        frame=FrameMetadata(
            width=100, height=100, source_id="api_upload", timestamp=datetime.now()
        ),
        defects=[],  # Simplified for this test
        decision=decision_mock.evaluate.return_value,
        defect_count=1,
        timestamp=datetime.now(),
    )
    mock_get_result.return_value = result_mock

    mock_get_plc.return_value = None  # PLC disabled

    # Act
    upload_file = MockUploadFile(valid_image_bytes)
    response = process_inspection(upload_file, "test_id")

    # Assert
    assert response.inspection_id == "test_id"
    assert response.decision == "REJECT"
    assert response.severity == "HIGH"
    assert response.plc.enabled is False
    assert response.latency_ms > 0


def test_process_inspection_invalid_image():
    upload_file = MockUploadFile(b"invalid_bytes")
    with pytest.raises(InvalidImageError):
        process_inspection(upload_file, "test_id")
