from datetime import datetime

import pytest

from src.decision.models import Decision, DecisionResult, Severity
from src.mapping.result_builder import ResultBuilder
from src.vision.detection import Detection


@pytest.fixture
def builder():
    return ResultBuilder()


def test_build_result(builder):
    detections = [
        Detection(
            class_id=0,
            class_name="scratches",
            confidence=0.9,
            x1=10,
            y1=10,
            x2=100,
            y2=100,
        )
    ]
    decision_res = DecisionResult(
        decision=Decision.PASS,
        severity=Severity.NONE,
        reason="OK",
        total_defects=1,
        affected_classes=["scratches"],
        highest_confidence=0.9,
        timestamp=datetime.utcnow(),
    )

    result = builder.build(1920, 1080, "test_cam", detections, decision_res)

    assert result.frame.width == 1920
    assert result.frame.height == 1080
    assert result.frame.source_id == "test_cam"
    assert len(result.defects) == 1
    assert result.decision.decision == Decision.PASS
    assert result.summary.total_defects == 1


def test_build_empty_result(builder):
    decision_res = DecisionResult(
        decision=Decision.PASS,
        severity=Severity.NONE,
        reason="OK",
        total_defects=0,
        affected_classes=[],
        highest_confidence=0.0,
        timestamp=datetime.utcnow(),
    )

    result = builder.build(1920, 1080, "test_cam", [], decision_res)

    assert len(result.defects) == 0
    assert result.summary.total_defects == 0
    assert result.decision.decision == Decision.PASS
