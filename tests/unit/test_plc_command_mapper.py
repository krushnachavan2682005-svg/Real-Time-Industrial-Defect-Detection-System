from datetime import datetime, timezone

import pytest

from src.core.exceptions import PLCConfigurationError
from src.decision.models import Decision, DecisionResult, Severity
from src.mapping.models import FrameMetadata, InspectionResult
from src.plc.command_mapper import PLCCommandMapper
from src.plc.models import (
    PLCCommandConfig,
    PLCCommandType,
    PLCConfig,
)


@pytest.fixture
def config():
    return PLCConfig(
        commands={
            "pass": PLCCommandConfig(action=PLCCommandType.CONTINUE_CONVEYOR),
            "review": PLCCommandConfig(
                action=PLCCommandType.FLAG_FOR_MANUAL_INSPECTION
            ),
            "reject": PLCCommandConfig(action=PLCCommandType.REJECT_PRODUCT),
        }
    )


@pytest.fixture
def mapper(config):
    return PLCCommandMapper(config)


def test_map_decision_pass(mapper):
    command = mapper.map_decision(Decision.PASS)
    assert command.command_type == PLCCommandType.CONTINUE_CONVEYOR
    assert command.metadata["source_decision"] == "PASS"


def test_map_decision_review(mapper):
    command = mapper.map_decision(Decision.REVIEW)
    assert command.command_type == PLCCommandType.FLAG_FOR_MANUAL_INSPECTION


def test_map_decision_reject(mapper):
    command = mapper.map_decision(Decision.REJECT)
    assert command.command_type == PLCCommandType.REJECT_PRODUCT


def test_map_decision_invalid_config():
    config = PLCConfig(commands={})
    mapper = PLCCommandMapper(config)
    with pytest.raises(PLCConfigurationError):
        mapper.map_decision(Decision.PASS)


def test_map_inspection_result(mapper):
    inspection = InspectionResult(
        frame=FrameMetadata(
            width=1, height=1, source_id="test", timestamp=datetime.now(timezone.utc)
        ),
        defects=[],
        decision=DecisionResult(
            decision=Decision.REJECT,
            severity=Severity.HIGH,
            reason="",
            total_defects=0,
            affected_classes=[],
            highest_confidence=0.0,
            timestamp=datetime.now(timezone.utc),
        ),
        defect_count=0,
        timestamp=datetime.now(timezone.utc),
    )
    command = mapper.map_inspection_result(inspection)
    assert command.command_type == PLCCommandType.REJECT_PRODUCT
    assert command.inspection_id is not None
