from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.core.exceptions import IntegrationError, PLCConnectionError
from src.decision.models import Decision, DecisionResult, Severity
from src.mapping.models import FrameMetadata, InspectionResult
from src.plc.models import PLCCommand, PLCCommandType, PLCResponse, PLCStatus
from src.plc.service import PLCService


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.health_check.return_value = PLCStatus.CONNECTED
    return client


@pytest.fixture
def mock_mapper():
    mapper = MagicMock()
    return mapper


@pytest.fixture
def service(mock_client, mock_mapper):
    return PLCService(mock_client, mock_mapper)


def test_service_start_stop(service, mock_client):
    service.start()
    mock_client.connect.assert_called_once()

    service.stop()
    mock_client.disconnect.assert_called_once()


def test_service_start_failure(service, mock_client):
    mock_client.connect.side_effect = PLCConnectionError("Connection failed")
    with pytest.raises(IntegrationError):
        service.start()


def test_process_inspection_success(service, mock_client, mock_mapper):
    inspection = InspectionResult(
        frame=FrameMetadata(
            width=1, height=1, source_id="test", timestamp=datetime.now(timezone.utc)
        ),
        defects=[],
        decision=DecisionResult(
            decision=Decision.PASS,
            severity=Severity.NONE,
            reason="",
            total_defects=0,
            affected_classes=[],
            highest_confidence=0.0,
            timestamp=datetime.now(timezone.utc),
        ),
        defect_count=0,
        timestamp=datetime.now(timezone.utc),
    )

    mock_command = PLCCommand(
        command_id="123", command_type=PLCCommandType.CONTINUE_CONVEYOR
    )
    mock_mapper.map_inspection_result.return_value = mock_command

    mock_response = PLCResponse(
        success=True, status=PLCStatus.CONNECTED, message="OK", command_id="123"
    )
    mock_client.send_command.return_value = mock_response

    response = service.process_inspection(inspection)

    assert response.success is True
    assert response.command_id == "123"
    mock_mapper.map_inspection_result.assert_called_once_with(inspection)
    mock_client.send_command.assert_called_once_with(mock_command)


def test_process_inspection_client_failure(service, mock_client, mock_mapper):
    inspection = InspectionResult(
        frame=FrameMetadata(
            width=1, height=1, source_id="test", timestamp=datetime.now(timezone.utc)
        ),
        defects=[],
        decision=DecisionResult(
            decision=Decision.PASS,
            severity=Severity.NONE,
            reason="",
            total_defects=0,
            affected_classes=[],
            highest_confidence=0.0,
            timestamp=datetime.now(timezone.utc),
        ),
        defect_count=0,
        timestamp=datetime.now(timezone.utc),
    )

    mock_command = PLCCommand(
        command_id="123", command_type=PLCCommandType.CONTINUE_CONVEYOR
    )
    mock_mapper.map_inspection_result.return_value = mock_command

    mock_client.send_command.side_effect = PLCConnectionError("Failed to send")

    response = service.process_inspection(inspection)

    assert response.success is False
    assert "Communication error" in response.message
