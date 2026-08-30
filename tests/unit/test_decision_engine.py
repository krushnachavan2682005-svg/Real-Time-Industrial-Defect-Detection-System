import os
import tempfile

import pytest
import yaml

from src.core.exceptions import DecisionError
from src.decision.decision_engine import DecisionEngine
from src.decision.models import Decision, Severity
from src.vision.detection import Detection


@pytest.fixture
def valid_config_yaml():
    config_dict = {
        "global_rules": {"minimum_confidence": 0.25, "max_allowed_defects": 5},
        "class_specific_rules": {
            "crazing": {"minimum_confidence": 0.30, "severity_if_found": "MEDIUM"},
            "pitted_surface": {"minimum_confidence": 0.40, "severity_if_found": "HIGH"},
            "rolled_in_scale": {
                "minimum_confidence": 0.35,
                "severity_if_found": "CRITICAL",
            },
        },
        "severity_escalation": {
            "multiple_defects_threshold": 3,
            "escalate_to": "MEDIUM",
        },
        "decision_policy": {
            "no_defects": "PASS",
            "low_severity": "REVIEW",
            "medium_severity": "REVIEW",
            "high_severity": "REJECT",
            "critical_severity": "REJECT",
        },
    }
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        yaml.dump(config_dict, f)
        temp_path = f.name

    yield temp_path
    os.remove(temp_path)


def test_decision_engine_initialization(valid_config_yaml):
    engine = DecisionEngine(valid_config_yaml)
    assert engine is not None


def test_decision_engine_invalid_config():
    with pytest.raises(DecisionError):
        DecisionEngine("non_existent_file.yaml")


def test_decision_engine_evaluate_no_defects(valid_config_yaml):
    engine = DecisionEngine(valid_config_yaml)
    result = engine.evaluate([])
    assert result.decision == Decision.PASS
    assert result.severity == Severity.NONE
    assert result.total_defects == 0


def test_decision_engine_evaluate_low_severity(valid_config_yaml):
    engine = DecisionEngine(valid_config_yaml)
    detections = [
        Detection(
            class_id=1, class_name="scratches", confidence=0.8, x1=0, y1=0, x2=10, y2=10
        )
    ]
    result = engine.evaluate(detections)
    assert result.decision == Decision.REVIEW
    assert result.severity == Severity.LOW


def test_decision_engine_evaluate_critical_class(valid_config_yaml):
    engine = DecisionEngine(valid_config_yaml)
    detections = [
        Detection(
            class_id=4,
            class_name="rolled_in_scale",
            confidence=0.9,
            x1=0,
            y1=0,
            x2=10,
            y2=10,
        )
    ]
    result = engine.evaluate(detections)
    assert result.decision == Decision.REJECT
    assert result.severity == Severity.CRITICAL


def test_decision_engine_aggregation_and_escalation(valid_config_yaml):
    engine = DecisionEngine(valid_config_yaml)
    # Provide 3 defects (scratches), threshold for escalation is 3 -> MEDIUM -> REVIEW
    detections = [
        Detection(
            class_id=1, class_name="scratches", confidence=0.8, x1=0, y1=0, x2=10, y2=10
        ),
        Detection(
            class_id=1, class_name="scratches", confidence=0.7, x1=0, y1=0, x2=10, y2=10
        ),
        Detection(
            class_id=2, class_name="patches", confidence=0.6, x1=0, y1=0, x2=10, y2=10
        ),
    ]
    result = engine.evaluate(detections)
    assert result.total_defects == 3
    assert result.severity == Severity.MEDIUM
    assert result.decision == Decision.REVIEW
