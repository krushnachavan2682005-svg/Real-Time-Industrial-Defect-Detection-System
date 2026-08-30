import pytest

from src.mapping.models import SpatialRegion
from src.mapping.spatial_mapper import SpatialMapper


@pytest.fixture
def mapper():
    return SpatialMapper(1920, 1080)


def test_calculate_center(mapper):
    cx, cy = mapper.calculate_center(100, 100, 300, 300)
    assert cx == 200.0
    assert cy == 200.0


def test_calculate_area(mapper):
    area = mapper.calculate_area(200, 200)
    assert area == 40000.0


def test_calculate_area_ratio(mapper):
    ratio = mapper.calculate_area_ratio(207360)
    assert ratio == 0.1  # 207360 / (1920 * 1080)


def test_validate_bbox(mapper):
    assert mapper.validate_bbox(10, 10, 100, 100) is True
    assert mapper.validate_bbox(100, 100, 10, 10) is False  # inverted

    bad_mapper = SpatialMapper(0, 0)
    assert bad_mapper.validate_bbox(10, 10, 100, 100) is False


def test_normalized_center(mapper):
    nx, ny = mapper.calculate_normalized_center(1920, 1080)
    assert nx == 1.0
    assert ny == 1.0

    nx, ny = mapper.calculate_normalized_center(-10, -10)
    assert nx == 0.0
    assert ny == 0.0


def test_regions(mapper):
    assert mapper.get_region(0.1, 0.1) == SpatialRegion.TOP_LEFT
    assert mapper.get_region(0.5, 0.5) == SpatialRegion.CENTER
    assert mapper.get_region(0.9, 0.9) == SpatialRegion.BOTTOM_RIGHT
    assert mapper.get_region(0.1, 0.9) == SpatialRegion.BOTTOM_LEFT
    assert mapper.get_region(0.9, 0.1) == SpatialRegion.TOP_RIGHT
