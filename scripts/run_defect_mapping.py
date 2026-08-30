import json
import os
from datetime import datetime

import cv2
import numpy as np

from src.decision.models import Decision, DecisionResult, Severity
from src.mapping.result_builder import ResultBuilder
from src.mapping.visualizer import DefectVisualizer
from src.vision.detection import Detection


def main():
    print("Running Defect Mapping Module...")

    os.makedirs("reports/mapping", exist_ok=True)

    # 1. Create a dummy frame
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

    # 2. Mock Detections
    detections = [
        Detection(
            class_id=0,
            class_name="scratches",
            confidence=0.91,
            x1=1500,
            y1=100,
            x2=1700,
            y2=300,
        ),
        Detection(
            class_id=2,
            class_name="patches",
            confidence=0.85,
            x1=800,
            y1=400,
            x2=1100,
            y2=700,
        ),
        Detection(
            class_id=1,
            class_name="crazing",
            confidence=0.72,
            x1=100,
            y1=800,
            x2=300,
            y2=1000,
        ),
    ]

    # 3. Mock DecisionResult
    decision_result = DecisionResult(
        decision=Decision.REJECT,
        severity=Severity.HIGH,
        reason="Multiple defects found",
        total_defects=3,
        affected_classes=["scratches", "patches", "crazing"],
        highest_confidence=0.91,
        timestamp=datetime.utcnow(),
    )

    # 4. Build Result
    builder = ResultBuilder()
    inspection_result = builder.build(
        frame_width=frame.shape[1],
        frame_height=frame.shape[0],
        source_id="cam_01",
        detections=detections,
        decision_result=decision_result,
    )

    # 5. Visualize
    visualizer = DefectVisualizer()
    annotated_frame = visualizer.render(frame, inspection_result)

    # 6. Save Artifacts
    json_path = "reports/mapping/inspection_result.json"
    img_path = "reports/mapping/annotated_frame.jpg"

    with open(json_path, "w") as f:
        # Pydantic v2 dump
        if hasattr(inspection_result, "model_dump_json"):
            f.write(inspection_result.model_dump_json(indent=2))
        else:
            f.write(inspection_result.json(indent=2))

    cv2.imwrite(img_path, annotated_frame)
    print(f"Artifacts saved to {json_path} and {img_path}")


if __name__ == "__main__":
    main()
