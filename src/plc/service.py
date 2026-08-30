import logging

from src.core.exceptions import IntegrationError, PLCConfigurationError
from src.mapping.models import InspectionResult
from src.plc.base import BasePLCClient
from src.plc.command_mapper import PLCCommandMapper
from src.plc.models import PLCResponse, PLCStatus

logger = logging.getLogger(__name__)


class PLCService:
    """Orchestrates communication with the PLC based on inspection results."""

    def __init__(self, client: BasePLCClient, mapper: PLCCommandMapper):
        self.client = client
        self.mapper = mapper

    def start(self) -> None:
        """Initialize the PLC connection."""
        try:
            self.client.connect()
        except IntegrationError as e:
            logger.error(f"Failed to start PLC service: {e}")
            raise

    def stop(self) -> None:
        """Close the PLC connection."""
        try:
            self.client.disconnect()
        except IntegrationError as e:
            logger.error(f"Error stopping PLC service: {e}")
            raise

    def process_inspection(self, result: InspectionResult) -> PLCResponse:
        """Process an inspection result and send the appropriate command to the PLC.

        Args:
            result: The structured inspection result from the mapping layer.

        Returns:
            The response from the PLC, indicating success or failure.
        """
        try:
            command = self.mapper.map_inspection_result(result)
        except PLCConfigurationError as e:
            logger.error(f"Command mapping failed: {e}")
            return PLCResponse(
                success=False,
                status=self.client.health_check(),
                message=f"Configuration error: {e}",
            )

        try:
            response = self.client.send_command(command)
            return response
        except IntegrationError as e:
            logger.error(f"PLC communication failed: {e}")
            return PLCResponse(
                success=False,
                status=self.client.health_check(),
                message=f"Communication error: {e}",
                command_id=command.command_id,
            )
        except Exception as e:
            logger.error(f"Unexpected error communicating with PLC: {e}")
            return PLCResponse(
                success=False,
                status=PLCStatus.ERROR,
                message=f"Unexpected error: {e}",
                command_id=command.command_id,
            )
