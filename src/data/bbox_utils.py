import math
from typing import Tuple


def xyxy_to_xywh(xmin: float, ymin: float, xmax: float, ymax: float) -> Tuple[float, float, float, float]:
    """
    Converts absolute [xmin, ymin, xmax, ymax] to [x_center, y_center, width, height].
    
    Returns:
        Tuple of (x_center, y_center, width, height).
    """
    x_center = (xmin + xmax) / 2.0
    y_center = (ymin + ymax) / 2.0
    width = xmax - xmin
    height = ymax - ymin

    return x_center, y_center, width, height


def normalize_bbox(
    x_center: float, y_center: float, width: float, height: float, image_width: float, image_height: float
) -> Tuple[float, float, float, float]:
    """
    Normalizes coordinates using image width and height.
    Values are clamped between 0.0 and 1.0.
    
    Raises:
        ValueError: If image_width or image_height is <= 0.
    """
    if image_width <= 0 or image_height <= 0:
        raise ValueError("Image dimensions must be positive.")

    x_center_norm = x_center / image_width
    y_center_norm = y_center / image_height
    width_norm = width / image_width
    height_norm = height / image_height

    # YOLO format requires normalized coordinates
    # We clip centers to [0.0, 1.0] to prevent out-of-bounds coordinates
    x_center_norm = max(0.0, min(1.0, x_center_norm))
    y_center_norm = max(0.0, min(1.0, y_center_norm))
    width_norm = max(0.0, min(1.0, width_norm))
    height_norm = max(0.0, min(1.0, height_norm))

    return x_center_norm, y_center_norm, width_norm, height_norm


def is_valid_xyxy(xmin: float, ymin: float, xmax: float, ymax: float) -> bool:
    """
    Checks if absolute coordinates form a valid bounding box.
    Returns False if area is zero/negative, or if values are NaN/Infinity.
    """
    coords = (xmin, ymin, xmax, ymax)
    if any(math.isnan(c) or math.isinf(c) for c in coords):
        return False

    if xmin >= xmax or ymin >= ymax:
        return False

    return True


def clip_xyxy(
    xmin: float, ymin: float, xmax: float, ymax: float, image_width: float, image_height: float
) -> Tuple[float, float, float, float]:
    """
    Clips absolute bounding box coordinates to image boundaries.
    """
    xmin = max(0.0, min(float(image_width), xmin))
    xmax = max(0.0, min(float(image_width), xmax))
    ymin = max(0.0, min(float(image_height), ymin))
    ymax = max(0.0, min(float(image_height), ymax))

    return xmin, ymin, xmax, ymax
