import pytest

from src.core.exceptions import PLCConnectionError
from src.plc.models import PLCCommand, PLCCommandType, PLCStatus
from src.plc.simulator import SimulationPLCClient


@pytest.fixture
def simulator():
    return SimulationPLCClient()


def test_initial_state(simulator):
    assert simulator.health_check() == PLCStatus.DISCONNECTED


def test_connect_disconnect(simulator):
    simulator.connect()
    assert simulator.health_check() == PLCStatus.CONNECTED

    simulator.disconnect()
    assert simulator.health_check() == PLCStatus.DISCONNECTED


def test_send_command_success(simulator):
    simulator.connect()
    command = PLCCommand(
        command_id="123", command_type=PLCCommandType.CONTINUE_CONVEYOR
    )
    response = simulator.send_command(command)

    assert response.success is True
    assert response.command_id == "123"
    assert response.status == PLCStatus.CONNECTED


def test_send_command_disconnected(simulator):
    command = PLCCommand(
        command_id="123", command_type=PLCCommandType.CONTINUE_CONVEYOR
    )
    with pytest.raises(PLCConnectionError):
        simulator.send_command(command)
