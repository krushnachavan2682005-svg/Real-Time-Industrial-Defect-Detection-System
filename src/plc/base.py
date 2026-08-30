from abc import ABC, abstractmethod

from src.plc.models import PLCCommand, PLCResponse, PLCStatus


class BasePLCClient(ABC):
    """Abstract interface for PLC communication."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the PLC."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the PLC."""
        pass

    @abstractmethod
    def send_command(self, command: PLCCommand) -> PLCResponse:
        """Send a command to the PLC and wait for a response.

        Args:
            command: The structured command to send.

        Returns:
            The structured response from the PLC.
        """
        pass

    @abstractmethod
    def health_check(self) -> PLCStatus:
        """Check the current connection status of the PLC."""
        pass
