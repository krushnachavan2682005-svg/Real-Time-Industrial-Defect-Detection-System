from datetime import datetime

import numpy as np
import pytest

from src.decision.models import Decision, DecisionResult, Severity
from src.mapping.models import (
    FrameMetadata,
    InspectionResult,
    InspectionSummary,
    MappedDefect,
    SpatialRegion,
)
from src.mapping.visualizer import DefectVisualizer


@pytest.fixture
def visualizer():
    return DefectVisualizer("fake/path/config.yaml")  # Fallback to default


def test_visualizer_render_pass(visualizer):
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = InspectionResult(
        frame=FrameMetadata(
            width=100, height=100, source_id="1", timestamp=datetime.utcnow()
        ),
        defects=[],
        decision=DecisionResult(
            decision=Decision.PASS,
            severity=Severity.NONE,
            reason="OK",
            total_defects=0,
            affected_classes=[],
            highest_confidence=0.0,
            timestamp=datetime.utcnow(),
        ),
        summary=InspectionSummary(total_defects=0, affected_regions=[]),
    )

    annotated = visualizer.render(frame, result)

    assert annotated.shape == frame.shape
    assert not np.array_equal(annotated, frame)  # Since it writes text


def test_visualizer_render_defects(visualizer):
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    det = {
        "class_id": 0,
        "class_name": "scratch",
        "confidence": 0.9,
        "bbox": [10, 10, 50, 50],
    }
    defect = MappedDefect(
        detection=det,
        center_x=30,
        center_y=30,
        normalized_center_x=0.3,
        normalized_center_y=0.3,
        width=40,
        height=40,
        area=1600,
        area_ratio=0.16,
        spatial_region=SpatialRegion.TOP_LEFT,
    )

    result = InspectionResult(
        frame=FrameMetadata(
            width=100, height=100, source_id="1", timestamp=datetime.utcnow()
        ),
        defects=[defect],
        decision=DecisionResult(
            decision=Decision.REJECT,
            severity=Severity.HIGH,
            reason="Bad",
            total_defects=1,
            affected_classes=["scratch"],
            highest_confidence=0.9,
            timestamp=datetime.utcnow(),
        ),
        summary=InspectionSummary(total_defects=1, affected_regions=["TOP_LEFT"]),
    )

    annotated = visualizer.render(frame, result)

    assert annotated.shape == frame.shape
    # Check that original frame is unmodified
    assert np.all(frame == 0)
