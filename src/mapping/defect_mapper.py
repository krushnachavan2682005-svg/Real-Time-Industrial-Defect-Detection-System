from typing import List

from src.mapping.models import MappedDefect
from src.mapping.spatial_mapper import SpatialMapper
from src.vision.detection import Detection


class DefectMapper:
    """Maps bounding box detections to spatial objects."""

    def __init__(self, frame_width: int, frame_height: int):
        self.spatial_mapper = SpatialMapper(frame_width, frame_height)

    def map_detections(self, detections: List[Detection]) -> List[MappedDefect]:
        mapped_defects = []
        for det in detections:
            valid = self.spatial_mapper.validate_bbox(det.x1, det.y1, det.x2, det.y2)
            if not valid:
                continue

            width = det.width
            height = det.height
            center_x, center_y = self.spatial_mapper.calculate_center(
                det.x1, det.y1, det.x2, det.y2
            )
            norm_x, norm_y = self.spatial_mapper.calculate_normalized_center(
                center_x, center_y
            )
            area = self.spatial_mapper.calculate_area(width, height)
            area_ratio = self.spatial_mapper.calculate_area_ratio(area)
            region = self.spatial_mapper.get_region(norm_x, norm_y)

            mapped = MappedDefect(
                detection=det.to_dict(),
                center_x=center_x,
                center_y=center_y,
                normalized_center_x=norm_x,
                normalized_center_y=norm_y,
                width=float(width),
                height=float(height),
                area=area,
                area_ratio=area_ratio,
                spatial_region=region,
            )
            mapped_defects.append(mapped)

        return mapped_defects
