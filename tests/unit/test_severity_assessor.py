import pytest

from src.decision.config import (
    ClassSpecificRuleConfig,
    DecisionPolicyConfig,
    DecisionRulesConfig,
    GlobalRulesConfig,
    SeverityEscalationConfig,
)
from src.decision.models import Decision, DefectSummary, Severity
from src.decision.severity_assessor import SeverityAssessor


@pytest.fixture
def mock_config():
    return DecisionRulesConfig(
        global_rules=GlobalRulesConfig(minimum_confidence=0.5, max_allowed_defects=3),
        class_specific_rules={
            "crazing": ClassSpecificRuleConfig(
                minimum_confidence=0.8, severity_if_found=Severity.HIGH
            ),
            "rolled_in_scale": ClassSpecificRuleConfig(
                minimum_confidence=0.5, severity_if_found=Severity.CRITICAL
            ),
        },
        severity_escalation=SeverityEscalationConfig(
            multiple_defects_threshold=2, escalate_to=Severity.MEDIUM
        ),
        decision_policy=DecisionPolicyConfig(
            no_defects=Decision.PASS,
            low_severity=Decision.REVIEW,
            medium_severity=Decision.REVIEW,
            high_severity=Decision.REJECT,
            critical_severity=Decision.REJECT,
        ),
    )


def test_assessor_no_defects(mock_config):
    assessor = SeverityAssessor(mock_config)
    summary = DefectSummary(
        total_defects=0,
        detections_by_class={},
        affected_classes=[],
        maximum_confidence=0.0,
        dominant_class=None,
    )
    sev, reason = assessor.assess(summary)
    assert sev == Severity.NONE
    assert "No defects" in reason


def test_assessor_low_severity_default(mock_config):
    assessor = SeverityAssessor(mock_config)
    summary = DefectSummary(
        total_defects=1,
        detections_by_class={"scratches": 1},
        affected_classes=["scratches"],
        maximum_confidence=0.6,
        dominant_class="scratches",
    )
    sev, reason = assessor.assess(summary)
    assert sev == Severity.LOW


def test_assessor_class_specific_severity(mock_config):
    assessor = SeverityAssessor(mock_config)
    summary = DefectSummary(
        total_defects=1,
        detections_by_class={"crazing": 1},
        affected_classes=["crazing"],
        maximum_confidence=0.9,
        dominant_class="crazing",
    )
    sev, reason = assessor.assess(summary)
    assert sev == Severity.HIGH
    assert "crazing" in reason


def test_assessor_escalation_multiple_defects(mock_config):
    assessor = SeverityAssessor(mock_config)
    # Threshold is 2, escalate to MEDIUM
    summary = DefectSummary(
        total_defects=2,
        detections_by_class={"scratches": 2},
        affected_classes=["scratches"],
        maximum_confidence=0.6,
        dominant_class="scratches",
    )
    sev, reason = assessor.assess(summary)
    assert sev == Severity.MEDIUM
    assert "escalated" in reason.lower()


def test_assessor_critical_class(mock_config):
    assessor = SeverityAssessor(mock_config)
    summary = DefectSummary(
        total_defects=1,
        detections_by_class={"rolled_in_scale": 1},
        affected_classes=["rolled_in_scale"],
        maximum_confidence=0.8,
        dominant_class="rolled_in_scale",
    )
    sev, reason = assessor.assess(summary)
    assert sev == Severity.CRITICAL


def test_assessor_exceeds_global_max(mock_config):
    assessor = SeverityAssessor(mock_config)
    # max allowed is 3, we have 4
    summary = DefectSummary(
        total_defects=4,
        detections_by_class={"scratches": 4},
        affected_classes=["scratches"],
        maximum_confidence=0.6,
        dominant_class="scratches",
    )
    sev, reason = assessor.assess(summary)
    assert sev == Severity.CRITICAL
    assert "exceeded global max allowed" in reason
