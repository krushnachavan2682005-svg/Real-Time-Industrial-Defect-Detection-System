from datetime import datetime

import numpy as np
import pytest

from src.core.exceptions import MappingError
from src.decision.models import Decision, DecisionResult, Severity
from src.mapping.defect_mapper import map_detections
from src.mapping.models import FrameMetadata, InspectionResult
from src.mapping.visualizer import Visualizer
from src.vision.detection import Detection


@pytest.fixture
def dummy_frame():
    return np.zeros((1080, 1920, 3), dtype=np.uint8)


@pytest.fixture
def dummy_inspection_result(dummy_frame):
    detections = [
        Detection(class_id=1, class_name="scratches", confidence=0.95, x1=100, y1=100, x2=300, y2=300)
    ]
    mapped = map_detections(detections, 1920, 1080)
    decision = DecisionResult(
        decision=Decision.REJECT,
        severity=Severity.HIGH,
        reason="Defects found",
        total_defects=1,
        affected_classes=["scratches"],
        highest_confidence=0.95,
        timestamp=datetime.utcnow()
    )
    return InspectionResult(
        frame=FrameMetadata(width=1920, height=1080, source_id="test", timestamp=datetime.utcnow()),
        defects=mapped,
        decision=decision,
        defect_count=1,
        timestamp=datetime.utcnow()
    )


def test_render_does_not_modify_original(dummy_frame, dummy_inspection_result):
    visualizer = Visualizer()
    frame_copy = dummy_frame.copy()
    
    annotated = visualizer.render(dummy_frame, dummy_inspection_result)
    
    # Check that original frame is unchanged
    assert np.array_equal(dummy_frame, frame_copy)
    # Check that returned frame is different
    assert not np.array_equal(annotated, dummy_frame)
    # Check that the returned frame has same shape
    assert annotated.shape == dummy_frame.shape


def test_render_empty_defects(dummy_frame):
    visualizer = Visualizer()
    decision = DecisionResult(
        decision=Decision.PASS,
        severity=Severity.NONE,
        reason="No defects",
        total_defects=0,
        affected_classes=[],
        highest_confidence=0.0,
        timestamp=datetime.utcnow()
    )
    empty_result = InspectionResult(
        frame=FrameMetadata(width=1920, height=1080, source_id="test", timestamp=datetime.utcnow()),
        defects=[],
        decision=decision,
        defect_count=0,
        timestamp=datetime.utcnow()
    )
    
    annotated = visualizer.render(dummy_frame, empty_result)
    assert annotated.shape == dummy_frame.shape
    # Frame is modified by text but no boxes


def test_render_invalid_frame(dummy_inspection_result):
    visualizer = Visualizer()
    with pytest.raises(MappingError):
        visualizer.render(None, dummy_inspection_result)
