import logging
from datetime import datetime
from typing import List

from src.core.exceptions import DecisionError
from src.decision.config import DecisionRulesConfig, load_decision_config
from src.decision.defect_aggregator import DefectAggregator
from src.decision.detection_filter import DetectionFilter
from src.decision.models import Decision, DecisionResult, Severity
from src.decision.severity_assessor import SeverityAssessor
from src.vision.detection import Detection

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Orchestrates the decision process based on defect detections."""

    def __init__(self, config_path: str):
        try:
            self.config: DecisionRulesConfig = load_decision_config(config_path)
            self.filter = DetectionFilter(self.config)
            self.aggregator = DefectAggregator()
            self.assessor = SeverityAssessor(self.config)
        except Exception as e:
            logger.error(f"Failed to initialize DecisionEngine: {e}")
            raise DecisionError(f"Decision Engine initialization failed: {e}") from e

    def evaluate(self, detections: List[Detection]) -> DecisionResult:
        """
        Evaluates a list of raw detections and returns a final industrial decision.
        """
        try:
            # Step 1: Filter raw detections based on configured confidence thresholds
            filtered_detections = self.filter.filter(detections)

            # Step 2: Aggregate the filtered detections into a summary
            summary = self.aggregator.aggregate(filtered_detections)

            # Step 3: Assess severity based on the summary
            severity, reason = self.assessor.assess(summary)

            # Step 4: Map severity to a final decision
            decision = self._apply_decision_policy(severity)

            # Construct the final result
            result = DecisionResult(
                decision=decision,
                severity=severity,
                reason=reason,
                total_defects=summary.total_defects,
                affected_classes=summary.affected_classes,
                highest_confidence=summary.maximum_confidence,
                timestamp=datetime.now(),
            )

            # Logging
            logger.info(
                f"Decision Engine evaluated {len(detections)} raw detections. "
                f"Filtered to {summary.total_defects} valid defects. "
                f"Result: {result.decision.name} (Severity: {result.severity.name})"
            )

            return result

        except Exception as e:
            logger.error(f"Error evaluating detections: {e}")
            raise DecisionError(f"Failed to evaluate detections: {e}") from e

    def _apply_decision_policy(self, severity: Severity) -> Decision:
        """Applies the configured policy to map a Severity to a Decision."""
        policy = self.config.decision_policy
        if severity == Severity.NONE:
            return policy.no_defects
        elif severity == Severity.LOW:
            return policy.low_severity
        elif severity == Severity.MEDIUM:
            return policy.medium_severity
        elif severity == Severity.HIGH:
            return policy.high_severity
        elif severity == Severity.CRITICAL:
            return policy.critical_severity

        # Fallback (should ideally never be reached if enum is exhausted)
        logger.warning(f"Unknown severity level '{severity}'. Defaulting to REJECT.")
        return Decision.REJECT
