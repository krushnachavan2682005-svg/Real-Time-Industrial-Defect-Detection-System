from typing import Tuple

from src.mapping.models import SpatialRegion


class SpatialMapper:
    """Calculates spatial features and regions from bounding boxes."""

    def __init__(self, frame_width: int, frame_height: int):
        self.frame_width = frame_width
        self.frame_height = frame_height

    def validate_bbox(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        if x1 >= x2 or y1 >= y2:
            return False
        if self.frame_width <= 0 or self.frame_height <= 0:
            return False
        return True

    def calculate_center(
        self, x1: int, y1: int, x2: int, y2: int
    ) -> Tuple[float, float]:
        return (x1 + x2) / 2.0, (y1 + y2) / 2.0

    def calculate_normalized_center(
        self, center_x: float, center_y: float
    ) -> Tuple[float, float]:
        norm_x = min(max(center_x / self.frame_width, 0.0), 1.0)
        norm_y = min(max(center_y / self.frame_height, 0.0), 1.0)
        return norm_x, norm_y

    def calculate_area(self, width: int, height: int) -> float:
        return float(width * height)

    def calculate_area_ratio(self, area: float) -> float:
        frame_area = self.frame_width * self.frame_height
        if frame_area == 0:
            return 0.0
        return area / frame_area

    def get_region(self, norm_x: float, norm_y: float) -> SpatialRegion:
        if norm_x < 0.33:
            if norm_y < 0.33:
                return SpatialRegion.TOP_LEFT
            elif norm_y < 0.66:
                return SpatialRegion.CENTER_LEFT
            else:
                return SpatialRegion.BOTTOM_LEFT
        elif norm_x < 0.66:
            if norm_y < 0.33:
                return SpatialRegion.TOP_CENTER
            elif norm_y < 0.66:
                return SpatialRegion.CENTER
            else:
                return SpatialRegion.BOTTOM_CENTER
        else:
            if norm_y < 0.33:
                return SpatialRegion.TOP_RIGHT
            elif norm_y < 0.66:
                return SpatialRegion.CENTER_RIGHT
            else:
                return SpatialRegion.BOTTOM_RIGHT
