import sys
from pathlib import Path

from rich.console import Console

# Ensure project root is in PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.decision.decision_engine import DecisionEngine
from src.vision.detection import Detection

console = Console()


def create_sample_detections(scenario: str) -> list[Detection]:
    if scenario == "no_defects":
        return []
    elif scenario == "low_confidence":
        return [
            Detection(
                class_id=0,
                class_name="crazing",
                confidence=0.10,
                x1=10,
                y1=10,
                x2=20,
                y2=20,
            )
        ]
    elif scenario == "low_severity":
        return [
            Detection(
                class_id=5,
                class_name="scratches",
                confidence=0.85,
                x1=50,
                y1=50,
                x2=100,
                y2=100,
            )
        ]
    elif scenario == "high_severity":
        return [
            Detection(
                class_id=3,
                class_name="pitted_surface",
                confidence=0.95,
                x1=0,
                y1=0,
                x2=200,
                y2=200,
            )
        ]
    elif scenario == "critical_defect":
        return [
            Detection(
                class_id=4,
                class_name="rolled_in_scale",
                confidence=0.90,
                x1=10,
                y1=10,
                x2=50,
                y2=50,
            )
        ]
    elif scenario == "multiple_defects":
        return [
            Detection(
                class_id=5,
                class_name="scratches",
                confidence=0.80,
                x1=0,
                y1=0,
                x2=10,
                y2=10,
            ),
            Detection(
                class_id=5,
                class_name="scratches",
                confidence=0.70,
                x1=20,
                y1=20,
                x2=30,
                y2=30,
            ),
            Detection(
                class_id=2,
                class_name="patches",
                confidence=0.85,
                x1=40,
                y1=40,
                x2=50,
                y2=50,
            ),
            Detection(
                class_id=1,
                class_name="inclusion",
                confidence=0.75,
                x1=60,
                y1=60,
                x2=70,
                y2=70,
            ),
        ]
    return []


def run():
    config_path = Path("configs/decision/decision_rules.yaml")
    if not config_path.exists():
        console.print(f"[red]Config file not found: {config_path}[/red]")
        sys.exit(1)

    console.print(f"Initializing Decision Engine with config: {config_path}")
    engine = DecisionEngine(str(config_path))

    scenarios = [
        "no_defects",
        "low_confidence",
        "low_severity",
        "high_severity",
        "critical_defect",
        "multiple_defects",
    ]

    for scenario in scenarios:
        console.print(f"\n[bold cyan]--- Scenario: {scenario.upper()} ---[/bold cyan]")
        detections = create_sample_detections(scenario)
        result = engine.evaluate(detections)

        color = (
            "green"
            if result.decision.value == "PASS"
            else "yellow" if result.decision.value == "REVIEW" else "red"
        )

        console.print(f"Decision: [bold {color}]{result.decision.name}[/bold {color}]")
        console.print(f"Severity: {result.severity.name}")
        console.print(f"Reason: {result.reason}")
        console.print(f"Total Valid Defects: {result.total_defects}")
        console.print(f"Affected Classes: {result.affected_classes}")


if __name__ == "__main__":
    run()
