from pathlib import Path
from typing import Dict, List

import yaml

from src.data.annotation_reader import ImageAnnotation
from src.data.bbox_utils import is_valid_xyxy


class AnnotationValidationError(Exception):
    """Exception raised when an annotation fails validation."""
    pass


def load_classes(classes_path: str | Path) -> Dict[str, int]:
    """Loads the canonical class mapping from a YAML file."""
    path = Path(classes_path)
    if not path.exists():
        raise FileNotFoundError(f"Classes file not found: {path}")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid classes format in {path}. Expected dictionary.")

    return data


def validate_annotation(annotation: ImageAnnotation, valid_classes: Dict[str, int]) -> List[str]:
    """
    Validates an ImageAnnotation.
    Returns a list of error messages for objects that are invalid, or empty list if all are valid.
    A valid annotation means:
    - the class is known
    - the bounding box has a positive area
    - the bounding box is within image boundaries (or can be clipped safely, but we check if it's completely outside)
    
    Raises:
        AnnotationValidationError: if the image dimensions are invalid or the annotation is fundamentally broken.
    """
    if annotation.image_width <= 0 or annotation.image_height <= 0:
        raise AnnotationValidationError(f"Invalid image dimensions: {annotation.image_width}x{annotation.image_height}")

    errors = []

    for idx, obj in enumerate(annotation.objects):
        if obj.class_name not in valid_classes:
            errors.append(f"Object {idx}: Unknown class '{obj.class_name}'")
            continue

        bbox = obj.bbox
        if not is_valid_xyxy(bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax):
            errors.append(f"Object {idx}: Invalid bounding box coordinates ({bbox.xmin}, {bbox.ymin}, {bbox.xmax}, {bbox.ymax})")
            continue

        # Check if box is completely outside the image
        if bbox.xmin >= annotation.image_width or bbox.ymin >= annotation.image_height or bbox.xmax <= 0 or bbox.ymax <= 0:
            errors.append(f"Object {idx}: Bounding box completely outside image boundaries")
            continue

    return errors
