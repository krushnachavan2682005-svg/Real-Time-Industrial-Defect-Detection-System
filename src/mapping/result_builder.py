from datetime import datetime
from typing import List

import numpy as np

from src.core.exceptions import MappingError
from src.decision.models import DecisionResult
from src.mapping.defect_mapper import map_detections
from src.mapping.models import FrameMetadata, InspectionResult
from src.vision.detection import Detection


class ResultBuilder:
    def __init__(self):
        pass

    def build(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        decision_result: DecisionResult,
        source_id: str = "camera_01",
    ) -> InspectionResult:
        """
        Builds a structured InspectionResult from frame, detections, and decisions.
        """
        if not isinstance(frame, np.ndarray) or frame.size == 0:
            raise MappingError("Invalid frame provided.")

        height, width = frame.shape[:2]

        frame_metadata = FrameMetadata(
            width=width, height=height, source_id=source_id, timestamp=datetime.utcnow()
        )

        mapped_defects = map_detections(detections, width, height)

        return InspectionResult(
            frame=frame_metadata,
            defects=mapped_defects,
            decision=decision_result,
            defect_count=len(mapped_defects),
            timestamp=datetime.utcnow(),
        )
