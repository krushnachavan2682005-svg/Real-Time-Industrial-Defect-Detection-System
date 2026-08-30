from typing import Dict, List

from src.decision.models import DefectSummary
from src.vision.detection import Detection


class DefectAggregator:
    """Aggregates filtered detections into a structured summary."""

    @staticmethod
    def aggregate(detections: List[Detection]) -> DefectSummary:
        """
        Calculates total defect count, detections per class, affected classes,
        maximum confidence, and identifies the dominant defect class.
        """
        if not detections:
            return DefectSummary(
                total_defects=0,
                detections_by_class={},
                affected_classes=[],
                maximum_confidence=0.0,
                dominant_class=None,
            )

        total_defects = len(detections)
        detections_by_class: Dict[str, int] = {}
        maximum_confidence = 0.0

        for det in detections:
            class_name = det.class_name
            if class_name not in detections_by_class:
                detections_by_class[class_name] = 0
            detections_by_class[class_name] += 1

            if det.confidence > maximum_confidence:
                maximum_confidence = det.confidence

        affected_classes = list(detections_by_class.keys())

        # Determine dominant class (the one with the most detections)
        dominant_class = max(detections_by_class.items(), key=lambda item: item[1])[0]

        return DefectSummary(
            total_defects=total_defects,
            detections_by_class=detections_by_class,
            affected_classes=affected_classes,
            maximum_confidence=maximum_confidence,
            dominant_class=dominant_class,
        )
