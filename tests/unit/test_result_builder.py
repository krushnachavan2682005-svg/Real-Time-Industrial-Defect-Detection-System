from datetime import datetime

import numpy as np
import pytest

from src.core.exceptions import MappingError
from src.decision.models import Decision, DecisionResult, Severity
from src.mapping.result_builder import ResultBuilder
from src.vision.detection import Detection


@pytest.fixture
def dummy_frame():
    return np.zeros((1080, 1920, 3), dtype=np.uint8)


@pytest.fixture
def dummy_decision_result():
    return DecisionResult(
        decision=Decision.PASS,
        severity=Severity.NONE,
        reason="No defects detected",
        total_defects=0,
        affected_classes=[],
        highest_confidence=0.0,
        timestamp=datetime.utcnow(),
    )


def test_build_empty(dummy_frame, dummy_decision_result):
    builder = ResultBuilder()
    result = builder.build(dummy_frame, [], dummy_decision_result)
    
    assert result.defect_count == 0
    assert len(result.defects) == 0
    assert result.decision.decision == Decision.PASS
    assert result.frame.width == 1920
    assert result.frame.height == 1080


def test_build_with_defects(dummy_frame):
    builder = ResultBuilder()
    detections = [
        Detection(class_id=1, class_name="scratches", confidence=0.9, x1=10, y1=10, x2=50, y2=50)
    ]
    decision_result = DecisionResult(
        decision=Decision.REJECT,
        severity=Severity.HIGH,
        reason="Defects detected",
        total_defects=1,
        affected_classes=["scratches"],
        highest_confidence=0.9,
        timestamp=datetime.utcnow(),
    )
    result = builder.build(dummy_frame, detections, decision_result)
    
    assert result.defect_count == 1
    assert len(result.defects) == 1
    assert result.decision.decision == Decision.REJECT
    assert result.defects[0].spatial_region == "TOP_LEFT"


def test_build_invalid_frame(dummy_decision_result):
    builder = ResultBuilder()
    with pytest.raises(MappingError):
        builder.build(None, [], dummy_decision_result)
    with pytest.raises(MappingError):
        builder.build(np.array([]), [], dummy_decision_result)
