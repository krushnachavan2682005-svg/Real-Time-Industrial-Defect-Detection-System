import pytest
import numpy as np
import os
import yaml
from pathlib import Path
from src.augmentation.bbox_validation import validate_yolo_bboxes
from src.augmentation.pipeline import AugmentationPipeline

@pytest.fixture
def mock_config(tmp_path):
    config = {
        "seed": 42,
        "bbox_format": "yolo",
        "min_visibility": 0.3,
        "horizontal_flip": {"enabled": True, "p": 1.0}, # Force flip to test bbox transform
        "vertical_flip": {"enabled": False},
        "shift_scale_rotate": {"enabled": False}
    }
    config_path = tmp_path / "train.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return str(config_path)

def test_validate_yolo_bboxes_valid():
    bboxes = [[0.5, 0.5, 0.2, 0.2]]
    labels = [0]
    v_b, v_l = validate_yolo_bboxes(bboxes, labels)
    assert len(v_b) == 1
    assert v_b[0] == [0.5, 0.5, 0.2, 0.2]
    assert v_l == [0]

def test_validate_yolo_bboxes_invalid_bounds():
    # Out of bounds center
    bboxes = [[1.5, 0.5, 0.2, 0.2], [0.5, 0.5, -0.2, 0.2], [0.5, 0.5, 0.2, 0.0]]
    labels = [0, 1, 2]
    v_b, v_l = validate_yolo_bboxes(bboxes, labels)
    assert len(v_b) == 0

def test_pipeline_creation_and_flip(mock_config):
    pipeline = AugmentationPipeline(mock_config)
    
    # 100x100 dummy image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    bboxes = [[0.2, 0.5, 0.1, 0.1]]  # Left side
    labels = [0]
    
    aug_image, aug_bboxes, aug_labels = pipeline(image, bboxes, labels)
    
    # Horizontal flip is p=1.0, so x_center 0.2 should become 0.8
    assert len(aug_bboxes) == 1
    assert pytest.approx(aug_bboxes[0][0]) == 0.8
    assert aug_bboxes[0][1] == 0.5
    assert aug_labels == [0]

def test_pipeline_empty_boxes(mock_config):
    pipeline = AugmentationPipeline(mock_config)
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    aug_image, aug_bboxes, aug_labels = pipeline(image, [], [])
    
    assert len(aug_bboxes) == 0
    assert len(aug_labels) == 0
    assert aug_image.shape == image.shape
