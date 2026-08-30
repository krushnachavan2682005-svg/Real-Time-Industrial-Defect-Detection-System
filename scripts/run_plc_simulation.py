import logging
from datetime import datetime, timezone

from src.decision.models import Decision, DecisionResult, Severity
from src.mapping.models import FrameMetadata, InspectionResult
from src.plc.command_mapper import PLCCommandMapper
from src.plc.factory import PLCFactory
from src.plc.models import (
    PLCCommandConfig,
    PLCCommandType,
    PLCConfig,
    PLCSimulationConfig,
)
from src.plc.service import PLCService

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def create_mock_inspection(decision: Decision) -> InspectionResult:
    """Create a mock inspection result for testing."""
    return InspectionResult(
        frame=FrameMetadata(
            width=640,
            height=480,
            source_id="camera_1",
            timestamp=datetime.now(timezone.utc),
        ),
        defects=[],
        decision=DecisionResult(
            decision=decision,
            severity=Severity.NONE if decision == Decision.PASS else Severity.HIGH,
            reason="Mock testing",
            total_defects=0,
            affected_classes=[],
            highest_confidence=0.9,
            timestamp=datetime.now(timezone.utc),
        ),
        defect_count=0,
        timestamp=datetime.now(timezone.utc),
    )


def main():
    logger.info("Initializing PLC Simulation...")

    config = PLCConfig(
        enabled=True,
        mode="simulation",
        simulation=PLCSimulationConfig(enabled=True),
        commands={
            "pass": PLCCommandConfig(action=PLCCommandType.CONTINUE_CONVEYOR),
            "review": PLCCommandConfig(
                action=PLCCommandType.FLAG_FOR_MANUAL_INSPECTION
            ),
            "reject": PLCCommandConfig(action=PLCCommandType.REJECT_PRODUCT),
        },
    )

    client = PLCFactory.create_client(config)
    mapper = PLCCommandMapper(config)
    service = PLCService(client, mapper)

    service.start()

    scenarios = [Decision.PASS, Decision.REVIEW, Decision.REJECT]

    for decision in scenarios:
        logger.info("-" * 40)
        logger.info(f"Running Scenario: {decision.value}")

        inspection = create_mock_inspection(decision)

        response = service.process_inspection(inspection)

        logger.info(f"Response Success: {response.success}")
        logger.info(f"Response Status: {response.status.value}")
        logger.info(f"Response Message: {response.message}")

    logger.info("-" * 40)
    service.stop()
    logger.info("Simulation completed.")


if __name__ == "__main__":
    main()
