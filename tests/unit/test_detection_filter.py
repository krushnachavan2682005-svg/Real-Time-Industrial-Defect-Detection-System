import pytest

from src.decision.config import (
    ClassSpecificRuleConfig,
    DecisionPolicyConfig,
    DecisionRulesConfig,
    GlobalRulesConfig,
    SeverityEscalationConfig,
)
from src.decision.detection_filter import DetectionFilter
from src.decision.models import Decision, Severity
from src.vision.detection import Detection


@pytest.fixture
def mock_config():
    return DecisionRulesConfig(
        global_rules=GlobalRulesConfig(minimum_confidence=0.5, max_allowed_defects=5),
        class_specific_rules={
            "crazing": ClassSpecificRuleConfig(
                minimum_confidence=0.8, severity_if_found=Severity.MEDIUM
            )
        },
        severity_escalation=SeverityEscalationConfig(
            multiple_defects_threshold=3, escalate_to=Severity.HIGH
        ),
        decision_policy=DecisionPolicyConfig(
            no_defects=Decision.PASS,
            low_severity=Decision.REVIEW,
            medium_severity=Decision.REVIEW,
            high_severity=Decision.REJECT,
            critical_severity=Decision.REJECT,
        ),
    )


def test_filter_empty_list(mock_config):
    flt = DetectionFilter(mock_config)
    assert flt.filter([]) == []


def test_filter_below_global_threshold(mock_config):
    flt = DetectionFilter(mock_config)
    detections = [
        Detection(
            class_id=1, class_name="scratches", confidence=0.4, x1=0, y1=0, x2=10, y2=10
        )
    ]
    assert len(flt.filter(detections)) == 0


def test_filter_above_global_threshold(mock_config):
    flt = DetectionFilter(mock_config)
    detections = [
        Detection(
            class_id=1, class_name="scratches", confidence=0.6, x1=0, y1=0, x2=10, y2=10
        )
    ]
    assert len(flt.filter(detections)) == 1


def test_filter_below_class_specific_threshold(mock_config):
    flt = DetectionFilter(mock_config)
    detections = [
        # Global is 0.5, but crazing requires 0.8
        Detection(
            class_id=0, class_name="crazing", confidence=0.7, x1=0, y1=0, x2=10, y2=10
        )
    ]
    assert len(flt.filter(detections)) == 0


def test_filter_above_class_specific_threshold(mock_config):
    flt = DetectionFilter(mock_config)
    detections = [
        Detection(
            class_id=0, class_name="crazing", confidence=0.9, x1=0, y1=0, x2=10, y2=10
        )
    ]
    assert len(flt.filter(detections)) == 1


def test_filter_invalid_confidence(mock_config):
    flt = DetectionFilter(mock_config)
    detections = [
        Detection(
            class_id=1, class_name="scratches", confidence=1.5, x1=0, y1=0, x2=10, y2=10
        ),
        Detection(
            class_id=1,
            class_name="scratches",
            confidence=-0.5,
            x1=0,
            y1=0,
            x2=10,
            y2=10,
        ),
    ]
    assert len(flt.filter(detections)) == 0
