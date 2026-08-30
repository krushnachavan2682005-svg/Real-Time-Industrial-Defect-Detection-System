from typing import Tuple

from src.core.exceptions import MappingError


def calculate_center(x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
    return (x1 + x2) // 2, (y1 + y2) // 2


def calculate_dimensions(x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
    width = x2 - x1
    height = y2 - y1
    if width < 0 or height < 0:
        raise MappingError(
            f"Invalid bounding box coordinates: ({x1}, {y1}, {x2}, {y2})"
        )
    return width, height


def calculate_area(width: int, height: int) -> int:
    return width * height


def calculate_area_ratio(
    defect_area: int, frame_width: int, frame_height: int
) -> float:
    if frame_width <= 0 or frame_height <= 0:
        raise MappingError(f"Invalid frame dimensions: ({frame_width}, {frame_height})")
    frame_area = frame_width * frame_height
    return defect_area / frame_area


def normalize_coordinates(
    x: int, y: int, frame_width: int, frame_height: int
) -> Tuple[float, float]:
    if frame_width <= 0 or frame_height <= 0:
        raise MappingError(f"Invalid frame dimensions: ({frame_width}, {frame_height})")
    norm_x = min(max(x / frame_width, 0.0), 1.0)
    norm_y = min(max(y / frame_height, 0.0), 1.0)
    return norm_x, norm_y


def get_spatial_region(norm_x: float, norm_y: float) -> str:
    """
    Maps normalized coordinates [0, 1] to a 3x3 grid region.
    """
    if not (0.0 <= norm_x <= 1.0) or not (0.0 <= norm_y <= 1.0):
        raise MappingError(
            f"Coordinates must be normalized between 0 and 1. Got: ({norm_x}, {norm_y})"
        )

    # Determine X region
    if norm_x < 1 / 3:
        x_region = "LEFT"
    elif norm_x < 2 / 3:
        x_region = "CENTER"
    else:
        x_region = "RIGHT"

    # Determine Y region
    if norm_y < 1 / 3:
        y_region = "TOP"
    elif norm_y < 2 / 3:
        y_region = "CENTER"
    else:
        y_region = "BOTTOM"

    if x_region == "CENTER" and y_region == "CENTER":
        return "CENTER"

    return f"{y_region}_{x_region}"
