import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def validate_yolo_bboxes(
    bboxes: List[List[float]], class_labels: List[int]
) -> Tuple[List[List[float]], List[int]]:
    """
    Validates YOLO bounding boxes after augmentation.
    YOLO format: [x_center, y_center, width, height] normalized in [0, 1].

    Args:
        bboxes: List of bounding boxes.
        class_labels: List of class IDs corresponding to bboxes.

    Returns:
        A tuple of (valid_bboxes, valid_labels).
    """
    valid_bboxes = []
    valid_labels = []

    for bbox, label in zip(bboxes, class_labels):
        if len(bbox) != 4:
            logger.warning(f"Invalid bbox length: {len(bbox)}")
            continue

        x_c, y_c, w, h = bbox

        # Check for NaNs or infinity
        if any(not isinstance(v, (int, float)) for v in bbox):
            continue

        # Check positive dimensions
        if w <= 0 or h <= 0:
            continue

        # Check normalized range bounds for center
        if not (0.0 <= x_c <= 1.0) or not (0.0 <= y_c <= 1.0):
            continue
            
        # The w and h can technically be slightly larger than 1.0 if not strictly clamped, 
        # but logically should be within reasonable bounds. We just clamp x,y,w,h to [0,1].
        x_c = max(0.0, min(1.0, x_c))
        y_c = max(0.0, min(1.0, y_c))
        w = max(0.0, min(1.0, w))
        h = max(0.0, min(1.0, h))

        valid_bboxes.append([x_c, y_c, w, h])
        valid_labels.append(label)

    return valid_bboxes, valid_labels
