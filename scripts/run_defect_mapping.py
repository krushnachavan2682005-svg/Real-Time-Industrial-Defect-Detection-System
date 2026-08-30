import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from src.decision.models import Decision, DecisionResult, Severity
from src.mapping.result_builder import ResultBuilder
from src.mapping.visualizer import Visualizer
from src.vision.detection import Detection


def run_demo():
    # 1. Create a dummy image or load one if available
    # For demo purposes, create a dummy image (e.g., synthetic metal surface)
    frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 200
    cv2.putText(
        frame,
        "Synthetic Metal Surface",
        (800, 500),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (100, 100, 100),
        2,
    )

    # 2. Mock detections
    detections = [
        Detection(
            class_id=1,
            class_name="scratches",
            confidence=0.92,
            x1=200,
            y1=150,
            x2=450,
            y2=180,
        ),
        Detection(
            class_id=2,
            class_name="patches",
            confidence=0.85,
            x1=1400,
            y1=600,
            x2=1600,
            y2=800,
        ),
    ]

    # 3. Mock decision engine result
    decision_result = DecisionResult(
        decision=Decision.REJECT,
        severity=Severity.HIGH,
        reason="Critical defects detected",
        total_defects=2,
        affected_classes=["scratches", "patches"],
        highest_confidence=0.92,
        timestamp=datetime.utcnow(),
    )

    # 4. Map defects and build result
    print("Building inspection result...")
    builder = ResultBuilder()
    inspection_result = builder.build(
        frame, detections, decision_result, source_id="camera_mock"
    )

    # 5. Visualize
    print("Visualizing results...")
    visualizer = Visualizer()
    annotated_frame = visualizer.render(frame, inspection_result)

    # 6. Save output
    output_dir = Path("reports/mapping")
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "inspection_result.json"
    img_path = output_dir / "annotated_frame.jpg"

    with open(json_path, "w") as f:
        # Pydantic model serialization
        f.write(inspection_result.model_dump_json(indent=4))

    cv2.imwrite(str(img_path), annotated_frame)

    print(f"Results saved to {output_dir}:")
    print(f" - {json_path}")
    print(f" - {img_path}")


if __name__ == "__main__":
    run_demo()
