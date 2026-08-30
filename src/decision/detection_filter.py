import logging
from typing import List

from src.decision.config import DecisionRulesConfig
from src.vision.detection import Detection

logger = logging.getLogger(__name__)


class DetectionFilter:
    """Filters incoming raw detections based on configured confidence thresholds."""

    def __init__(self, config: DecisionRulesConfig):
        self.config = config

    def filter(self, detections: List[Detection]) -> List[Detection]:
        """
        Applies global and class-specific confidence thresholds to detections.
        Validates confidence bounds (0.0 to 1.0).
        """
        if not detections:
            return []

        filtered = []
        for det in detections:
            # Validate detection fields loosely if necessary
            if det.confidence < 0.0 or det.confidence > 1.0:
                logger.warning(
                    f"Invalid confidence value: {det.confidence}. Skipping detection."
                )
                continue

            # Determine threshold
            class_name = det.class_name
            threshold = self.config.global_rules.minimum_confidence

            if class_name in self.config.class_specific_rules:
                threshold = self.config.class_specific_rules[
                    class_name
                ].minimum_confidence

            if det.confidence >= threshold:
                filtered.append(det)

        return filtered
