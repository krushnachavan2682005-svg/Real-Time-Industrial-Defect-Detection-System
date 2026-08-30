from datetime import datetime
from typing import List

from src.decision.models import DecisionResult
from src.mapping.defect_mapper import DefectMapper
from src.mapping.models import (
    FrameMetadata,
    InspectionResult,
    InspectionSummary,
)
from src.vision.detection import Detection


class ResultBuilder:
    """Orchestrates building the InspectionResult."""

    def build(
        self,
        frame_width: int,
        frame_height: int,
        source_id: str,
        detections: List[Detection],
        decision_result: DecisionResult,
    ) -> InspectionResult:
        mapper = DefectMapper(frame_width, frame_height)
        mapped_defects = mapper.map_detections(detections)

        frame_meta = FrameMetadata(
            width=frame_width,
            height=frame_height,
            source_id=source_id,
            timestamp=datetime.utcnow(),
        )

        regions = list(set([d.spatial_region.value for d in mapped_defects]))

        summary = InspectionSummary(
            total_defects=len(mapped_defects), affected_regions=regions
        )

        return InspectionResult(
            frame=frame_meta,
            defects=mapped_defects,
            decision=decision_result,
            summary=summary,
        )
