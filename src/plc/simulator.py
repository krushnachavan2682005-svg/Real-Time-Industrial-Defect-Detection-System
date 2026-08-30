import logging
import time

from src.core.exceptions import PLCConnectionError
from src.plc.base import BasePLCClient
from src.plc.models import PLCCommand, PLCResponse, PLCStatus

logger = logging.getLogger(__name__)


class SimulationPLCClient(BasePLCClient):
    """A simulated PLC client for development and testing."""

    def __init__(self) -> None:
        self._status: PLCStatus = PLCStatus.DISCONNECTED

    def connect(self) -> None:
        """Simulate connecting to a PLC."""
        if self._status == PLCStatus.CONNECTED:
            logger.warning("[SIMULATION] PLC already connected.")
            return

        logger.info("[SIMULATION] Connecting to PLC...")
        time.sleep(0.1)  # Simulate network latency
        self._status = PLCStatus.CONNECTED
        logger.info("[SIMULATION] PLC connected successfully.")

    def disconnect(self) -> None:
        """Simulate disconnecting from a PLC."""
        if self._status == PLCStatus.DISCONNECTED:
            return

        logger.info("[SIMULATION] Disconnecting from PLC...")
        self._status = PLCStatus.DISCONNECTED
        logger.info("[SIMULATION] PLC disconnected.")

    def send_command(self, command: PLCCommand) -> PLCResponse:
        """Simulate sending a command to a PLC."""
        if self._status != PLCStatus.CONNECTED:
            logger.error("[SIMULATION] Attempted to send command while disconnected.")
            raise PLCConnectionError("Cannot send command: PLC is disconnected.")

        logger.info(
            f"[SIMULATION] Sending command: {command.command_type.value} "
            f"(ID: {command.command_id})"
        )

        time.sleep(0.05)  # Simulate execution latency

        # In a real simulation, we might have simulated failure states based on config,
        # but for now we always succeed if connected.

        logger.info(
            f"[SIMULATION] Command {command.command_type.value} completed successfully."
        )

        return PLCResponse(
            success=True,
            status=PLCStatus.CONNECTED,
            message=f"Simulated {command.command_type.value} executed",
            command_id=command.command_id,
        )

    def health_check(self) -> PLCStatus:
        """Check the simulated health status."""
        return self._status
