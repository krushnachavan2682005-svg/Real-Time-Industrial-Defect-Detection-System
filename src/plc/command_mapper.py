import uuid
from typing import Optional

from src.core.exceptions import PLCConfigurationError
from src.decision.models import Decision
from src.mapping.models import InspectionResult
from src.plc.models import PLCCommand, PLCConfig


class PLCCommandMapper:
    """Maps application decisions to industrial PLC commands based on configuration."""

    def __init__(self, config: PLCConfig):
        self.config = config

    def map_inspection_result(self, result: InspectionResult) -> PLCCommand:
        """Map an InspectionResult to a PLCCommand."""
        # InspectionResult doesn't inherently have an ID, we could use frame source_id
        # or timestamp if we wanted, but None is fine as it's optional.
        inspection_id = f"{result.frame.source_id}_{result.frame.timestamp.isoformat()}"
        return self.map_decision(
            decision=result.decision.decision,
            inspection_id=inspection_id,
        )

    def map_decision(
        self, decision: Decision, inspection_id: Optional[str] = None
    ) -> PLCCommand:
        """Map a Decision enum to a PLCCommand."""
        decision_key = decision.value.lower()

        if decision_key not in self.config.commands:
            raise PLCConfigurationError(
                f"No PLC command mapping found for decision: {decision.value}"
            )

        command_config = self.config.commands[decision_key]

        return PLCCommand(
            command_id=str(uuid.uuid4()),
            command_type=command_config.action,
            inspection_id=inspection_id,
            metadata={"source_decision": decision.value},
        )
