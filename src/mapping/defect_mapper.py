from typing import List

from src.mapping.models import MappedDefect
from src.mapping.spatial_mapper import (
    calculate_area,
    calculate_area_ratio,
    calculate_center,
    calculate_dimensions,
    get_spatial_region,
    normalize_coordinates,
)
from src.vision.detection import Detection


def map_detections(
    detections: List[Detection], frame_width: int, frame_height: int
) -> List[MappedDefect]:
    """
    Converts a list of raw Detections into MappedDefects with spatial context.
    """
    mapped_defects = []

    for det in detections:
        # Calculate spatial properties
        center_x, center_y = calculate_center(det.x1, det.y1, det.x2, det.y2)
        width, height = calculate_dimensions(det.x1, det.y1, det.x2, det.y2)
        area = calculate_area(width, height)
        area_ratio = calculate_area_ratio(area, frame_width, frame_height)

        norm_x, norm_y = normalize_coordinates(
            center_x, center_y, frame_width, frame_height
        )
        region = get_spatial_region(norm_x, norm_y)

        mapped = MappedDefect(
            original_detection=det.to_dict(),
            center_x=center_x,
            center_y=center_y,
            normalized_center_x=norm_x,
            normalized_center_y=norm_y,
            width=width,
            height=height,
            area=area,
            area_ratio=area_ratio,
            spatial_region=region,
        )
        mapped_defects.append(mapped)

    return mapped_defects
