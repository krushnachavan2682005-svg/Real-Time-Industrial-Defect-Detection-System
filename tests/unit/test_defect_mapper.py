from src.mapping.defect_mapper import map_detections
from src.vision.detection import Detection


def test_map_detections_empty():
    mapped = map_detections([], 1920, 1080)
    assert len(mapped) == 0


def test_map_detections_single():
    detections = [
        Detection(
            class_id=1,
            class_name="scratches",
            confidence=0.9,
            x1=100,
            y1=100,
            x2=300,
            y2=300,
        )
    ]
    mapped = map_detections(detections, 1000, 1000)
    assert len(mapped) == 1
    defect = mapped[0]
    assert defect.center_x == 200
    assert defect.center_y == 200
    assert defect.normalized_center_x == 0.2
    assert defect.normalized_center_y == 0.2
    assert defect.width == 200
    assert defect.height == 200
    assert defect.area == 40000
    assert defect.area_ratio == 0.04
    assert defect.spatial_region == "TOP_LEFT"
    assert defect.original_detection["class_name"] == "scratches"


def test_map_detections_multiple():
    detections = [
        Detection(class_id=1, class_name="scratches", confidence=0.9, x1=10, y1=10, x2=20, y2=20),
        Detection(class_id=2, class_name="patches", confidence=0.8, x1=500, y1=500, x2=600, y2=600),
    ]
    mapped = map_detections(detections, 1000, 1000)
    assert len(mapped) == 2
    assert mapped[0].spatial_region == "TOP_LEFT"
    assert mapped[1].spatial_region == "CENTER"
