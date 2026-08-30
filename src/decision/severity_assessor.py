from typing import Tuple

from src.decision.config import DecisionRulesConfig
from src.decision.models import DefectSummary, Severity


class SeverityAssessor:
    """Evaluates the severity of a set of defects based on configuration rules."""

    def __init__(self, config: DecisionRulesConfig):
        self.config = config

    def assess(self, summary: DefectSummary) -> Tuple[Severity, str]:
        """
        Assesses the severity and provides a reason string.
        Returns:
            Tuple containing the assessed Severity enum and a reason string.
        """
        if summary.total_defects == 0:
            return Severity.NONE, "No defects detected."

        # Initialize with lowest possible severity for defective items
        max_severity = Severity.LOW
        reason = "Defect(s) detected with low severity."

        severity_levels = {
            Severity.NONE: 0,
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4,
        }

        # Check class-specific rules
        for class_name in summary.affected_classes:
            if class_name in self.config.class_specific_rules:
                class_severity = self.config.class_specific_rules[
                    class_name
                ].severity_if_found
                if severity_levels[class_severity] > severity_levels[max_severity]:
                    max_severity = class_severity
                    reason = f"Detected defect class '{class_name}' with configured severity {class_severity.name}."

        # Check multiple defects escalation
        escalation_threshold = (
            self.config.severity_escalation.multiple_defects_threshold
        )
        if summary.total_defects >= escalation_threshold:
            escalated_severity = self.config.severity_escalation.escalate_to
            if severity_levels[escalated_severity] > severity_levels[max_severity]:
                max_severity = escalated_severity
                reason = f"Severity escalated to {escalated_severity.name} due to multiple defects ({summary.total_defects} >= {escalation_threshold})."

        # Check maximum allowed defects global rule (immediate critical/reject equivalent, but let's handle via severity or final decision)
        # Note: Depending on interpretation, exceeding max_allowed_defects might be a CRITICAL severity.
        # We will escalate to CRITICAL here if it exceeds global max.
        if summary.total_defects > self.config.global_rules.max_allowed_defects:
            max_severity = Severity.CRITICAL
            reason = f"Severity escalated to CRITICAL: total defects ({summary.total_defects}) exceeded global max allowed ({self.config.global_rules.max_allowed_defects})."

        return max_severity, reason
