import pytest

from src.mapping.defect_mapper import DefectMapper
from src.mapping.models import SpatialRegion
from src.vision.detection import Detection


@pytest.fixture
def mapper():
    return DefectMapper(1920, 1080)


def test_map_valid_detections(mapper):
    detections = [
        Detection(
            class_id=0,
            class_name="scratches",
            confidence=0.9,
            x1=0,
            y1=0,
            x2=640,
            y2=360,
        )
    ]

    mapped = mapper.map_detections(detections)

    assert len(mapped) == 1
    m = mapped[0]

    assert m.width == 640
    assert m.height == 360
    assert m.center_x == 320.0
    assert m.center_y == 180.0
    assert m.normalized_center_x == pytest.approx(0.1666, 0.01)
    assert m.normalized_center_y == pytest.approx(0.1666, 0.01)
    assert m.spatial_region == SpatialRegion.TOP_LEFT
    assert m.area == 640 * 360


def test_map_empty_detections(mapper):
    mapped = mapper.map_detections([])
    assert len(mapped) == 0


def test_map_invalid_detections(mapper):
    detections = [
        Detection(
            class_id=0,
            class_name="scratches",
            confidence=0.9,
            x1=100,
            y1=100,
            x2=10,
            y2=10,
        )  # invalid
    ]
    mapped = mapper.map_detections(detections)
    assert len(mapped) == 0
