import pytest
import math
from src.data.bbox_utils import (
    xyxy_to_xywh,
    normalize_bbox,
    is_valid_xyxy,
    clip_xyxy,
)


def test_xyxy_to_xywh():
    xmin, ymin, xmax, ymax = 10, 20, 50, 60
    x_center, y_center, width, height = xyxy_to_xywh(xmin, ymin, xmax, ymax)
    assert x_center == 30.0
    assert y_center == 40.0
    assert width == 40.0
    assert height == 40.0


def test_normalize_bbox_valid():
    x_center, y_center, width, height = 100.0, 100.0, 50.0, 50.0
    image_width, image_height = 200.0, 200.0
    xn, yn, wn, hn = normalize_bbox(x_center, y_center, width, height, image_width, image_height)
    
    assert xn == 0.5
    assert yn == 0.5
    assert wn == 0.25
    assert hn == 0.25


def test_normalize_bbox_out_of_bounds_clipping():
    x_center, y_center, width, height = 250.0, -10.0, 300.0, 50.0
    image_width, image_height = 200.0, 200.0
    xn, yn, wn, hn = normalize_bbox(x_center, y_center, width, height, image_width, image_height)
    
    assert xn == 1.0  # clipped
    assert yn == 0.0  # clipped
    assert wn == 1.0  # clipped
    assert hn == 0.25


def test_normalize_bbox_invalid_image_dims():
    with pytest.raises(ValueError):
        normalize_bbox(10, 10, 5, 5, 0, 200)
        
    with pytest.raises(ValueError):
        normalize_bbox(10, 10, 5, 5, 200, -10)


def test_is_valid_xyxy_valid():
    assert is_valid_xyxy(10, 10, 20, 20) is True


def test_is_valid_xyxy_zero_area():
    assert is_valid_xyxy(10, 10, 10, 20) is False
    assert is_valid_xyxy(10, 10, 20, 10) is False


def test_is_valid_xyxy_reversed_coords():
    assert is_valid_xyxy(20, 10, 10, 20) is False
    assert is_valid_xyxy(10, 20, 20, 10) is False


def test_is_valid_xyxy_nan_inf():
    assert is_valid_xyxy(float('nan'), 10, 20, 20) is False
    assert is_valid_xyxy(10, float('inf'), 20, 20) is False


def test_clip_xyxy():
    xmin, ymin, xmax, ymax = -10, 20, 250, 300
    image_width, image_height = 200, 200
    cx_min, cy_min, cx_max, cy_max = clip_xyxy(xmin, ymin, xmax, ymax, image_width, image_height)
    
    assert cx_min == 0.0
    assert cy_min == 20.0
    assert cx_max == 200.0
    assert cy_max == 200.0
