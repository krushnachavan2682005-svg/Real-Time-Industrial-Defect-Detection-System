from unittest.mock import MagicMock, patch

import numpy as np

from src.vision.camera import Camera
from src.vision.coordinate_transform import CoordinateTransformer
from src.vision.detection import Detection
from src.vision.postprocess import Postprocessor


def test_coordinate_transform():
    # Model 200x200, Orig 1000x1000 (Scale 5x)
    transformer = CoordinateTransformer((1000, 1000), (200, 200))
    x1, y1, x2, y2 = transformer.transform(10, 10, 20, 20)
    assert (x1, y1, x2, y2) == (50, 50, 100, 100)

    # Test clipping and ordering
    x1, y1, x2, y2 = transformer.transform(-10, 250, 250, -10)
    assert x1 == 0
    assert y1 == 0
    assert x2 == 999
    assert y2 == 999


def test_coordinate_transform_clip_valid():
    transformer = CoordinateTransformer((100, 100), (50, 50))  # Scale 2x
    x1, y1, x2, y2 = transformer.transform(-10, -10, -5, -5)
    # tx1=0, ty1=0, tx2=0, ty2=0 initially from clip
    # then check validity -> x2=1, y2=1
    assert (x1, y1, x2, y2) == (0, 0, 1, 1)


def test_postprocessor():
    class_map = {0: "test_class"}
    postprocessor = Postprocessor(class_map, conf_threshold=0.5, iou_threshold=0.5)

    # Create fake raw ONNX output: [1, 5, 2] (batch, 4_coords + 1_class, 2_anchors)
    raw_output = np.zeros((1, 5, 2))

    # Anchor 0: high confidence
    raw_output[0, 0, 0] = 50  # cx
    raw_output[0, 1, 0] = 50  # cy
    raw_output[0, 2, 0] = 20  # w
    raw_output[0, 3, 0] = 20  # h
    raw_output[0, 4, 0] = 0.9  # conf

    # Anchor 1: low confidence
    raw_output[0, 0, 1] = 10
    raw_output[0, 1, 1] = 10
    raw_output[0, 2, 1] = 5
    raw_output[0, 3, 1] = 5
    raw_output[0, 4, 1] = 0.1  # below thresh

    detections = postprocessor.process(raw_output)
    assert len(detections) == 1
    assert detections[0].class_id == 0
    assert detections[0].confidence == 0.9
    # cx=50, w=20 -> x1=40, x2=60
    assert detections[0].x1 == 40
    assert detections[0].x2 == 60


@patch("src.vision.camera.cv2.VideoCapture")
def test_camera_mock(mock_video_capture):
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    # Fake frame
    fake_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_cap.read.return_value = (True, fake_frame)
    mock_video_capture.return_value = mock_cap

    cam = Camera(0)
    assert cam.open()
    frame = cam.read()
    assert frame is not None
    assert frame.shape == (100, 100, 3)


def test_detection_dataclass():
    d = Detection(0, "scratches", 0.9, 10, 10, 30, 40)
    assert d.width == 20
    assert d.height == 30
    assert d.to_dict()["class_name"] == "scratches"
