from typing import Dict, List

from src.data.annotation_reader import ImageAnnotation
from src.data.bbox_utils import clip_xyxy, normalize_bbox, xyxy_to_xywh


class ConversionError(Exception):
    """Exception raised when an annotation cannot be converted."""
    pass

def convert_to_yolo(annotation: ImageAnnotation, valid_classes: Dict[str, int]) -> List[str]:
    """
    Converts a valid ImageAnnotation to a list of YOLO formatted strings.
    
    YOLO format:
    <class_id> <x_center> <y_center> <width> <height>
    
    Coordinates are normalized to [0, 1].
    
    Raises:
        ConversionError: if a class ID is missing or other conversion logic fails.
    """
    yolo_lines = []

    img_w = annotation.image_width
    img_h = annotation.image_height

    if img_w <= 0 or img_h <= 0:
        raise ConversionError(f"Cannot convert with invalid image dimensions {img_w}x{img_h}")

    for obj in annotation.objects:
        class_name = obj.class_name
        if class_name not in valid_classes:
            raise ConversionError(f"Cannot convert unknown class '{class_name}'")

        class_id = valid_classes[class_name]

        # 1. Clip bounding box to image dimensions
        xmin, ymin, xmax, ymax = clip_xyxy(
            obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax,
            img_w, img_h
        )

        # 2. Convert to xywh
        x_center, y_center, width, height = xyxy_to_xywh(xmin, ymin, xmax, ymax)

        # 3. Normalize
        try:
            x_center_norm, y_center_norm, width_norm, height_norm = normalize_bbox(
                x_center, y_center, width, height, img_w, img_h
            )
        except ValueError as e:
            raise ConversionError(f"Normalization failed: {e}")

        # Format string (using 6 decimal places for precision)
        line = f"{class_id} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}"
        yolo_lines.append(line)

    return yolo_lines
