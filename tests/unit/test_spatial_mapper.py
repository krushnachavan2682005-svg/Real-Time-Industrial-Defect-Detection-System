import pytest

from src.core.exceptions import MappingError
from src.mapping.spatial_mapper import (
    calculate_area,
    calculate_area_ratio,
    calculate_center,
    calculate_dimensions,
    get_spatial_region,
    normalize_coordinates,
)


def test_calculate_center():
    assert calculate_center(0, 0, 100, 100) == (50, 50)
    assert calculate_center(10, 20, 30, 40) == (20, 30)


def test_calculate_dimensions():
    assert calculate_dimensions(10, 20, 110, 120) == (100, 100)
    with pytest.raises(MappingError):
        calculate_dimensions(110, 120, 10, 20)  # Inverted coords


def test_calculate_area():
    assert calculate_area(10, 20) == 200
    assert calculate_area(0, 5) == 0


def test_calculate_area_ratio():
    assert calculate_area_ratio(100, 1000, 1000) == 0.0001
    with pytest.raises(MappingError):
        calculate_area_ratio(100, 0, 100)


def test_normalize_coordinates():
    assert normalize_coordinates(500, 500, 1000, 1000) == (0.5, 0.5)
    # Outside bounds should be clamped
    assert normalize_coordinates(1500, -100, 1000, 1000) == (1.0, 0.0)


def test_get_spatial_region():
    assert get_spatial_region(0.1, 0.1) == "TOP_LEFT"
    assert get_spatial_region(0.5, 0.1) == "TOP_CENTER"
    assert get_spatial_region(0.9, 0.1) == "TOP_RIGHT"
    
    assert get_spatial_region(0.1, 0.5) == "CENTER_LEFT"
    assert get_spatial_region(0.5, 0.5) == "CENTER"
    assert get_spatial_region(0.9, 0.5) == "CENTER_RIGHT"
    
    assert get_spatial_region(0.1, 0.9) == "BOTTOM_LEFT"
    assert get_spatial_region(0.5, 0.9) == "BOTTOM_CENTER"
    assert get_spatial_region(0.9, 0.9) == "BOTTOM_RIGHT"

    with pytest.raises(MappingError):
        get_spatial_region(1.5, 0.5)
