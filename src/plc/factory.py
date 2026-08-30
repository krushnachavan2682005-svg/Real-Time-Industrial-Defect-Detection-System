from src.core.exceptions import UnsupportedPLCModeError
from src.plc.base import BasePLCClient
from src.plc.models import PLCConfig
from src.plc.simulator import SimulationPLCClient


class PLCFactory:
    """Factory for creating PLC clients based on configuration."""

    @staticmethod
    def create_client(config: PLCConfig) -> BasePLCClient:
        """Create and return a PLC client based on the configured mode."""
        if config.mode.lower() == "simulation":
            if not config.simulation.enabled:
                raise UnsupportedPLCModeError(
                    "Simulation mode is selected but simulation is "
                    "not enabled in config."
                )
            return SimulationPLCClient()

        # Future support for modbus, opc-ua, etc.
        raise UnsupportedPLCModeError(f"Unsupported PLC mode: {config.mode}")
