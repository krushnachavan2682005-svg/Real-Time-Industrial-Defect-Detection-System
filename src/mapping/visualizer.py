import os
from typing import Tuple

import cv2
import numpy as np
import yaml

from src.decision.models import Decision
from src.mapping.models import InspectionResult


class DefectVisualizer:
    """Visualizes InspectionResult onto a frame."""

    def __init__(self, config_path: str = "configs/mapping/visualization.yaml"):
        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> dict:
        if os.path.exists(path):
            with open(path, "r") as f:
                import typing
                return typing.cast(dict, yaml.safe_load(f))
        # Default fallback
        return {
            "colors": {
                "pass": [0, 255, 0],
                "review": [0, 255, 255],
                "reject": [0, 0, 255],
                "default_box": [255, 255, 255],
                "text": [255, 255, 255],
                "text_bg": [0, 0, 0],
            },
            "drawing": {
                "box_thickness": 2,
                "font_scale_label": 0.5,
                "font_scale_main": 1.0,
                "font_thickness": 2,
            },
        }

    def _get_decision_color(self, decision: Decision) -> Tuple[int, int, int]:
        colors = self.config.get("colors", {})
        if decision == Decision.PASS:
            c = colors.get("pass", [0, 255, 0])
        elif decision == Decision.REVIEW:
            c = colors.get("review", [0, 255, 255])
        else:
            c = colors.get("reject", [0, 0, 255])
        return tuple(c)

    def render(self, frame: np.ndarray, result: InspectionResult) -> np.ndarray:
        """Draws annotations without mutating original frame."""
        annotated = frame.copy()

        box_thickness = self.config["drawing"]["box_thickness"]
        label_scale = self.config["drawing"]["font_scale_label"]
        txt_color = tuple(self.config["colors"]["text"])
        bg_color = tuple(self.config["colors"]["text_bg"])

        decision_color = self._get_decision_color(result.decision.decision)

        # Draw defects
        for defect in result.defects:
            bbox = defect.detection["bbox"]
            x1, y1, x2, y2 = [int(v) for v in bbox]
            cls_name = defect.detection["class_name"]
            conf = defect.detection["confidence"]
            region = defect.spatial_region.value

            cv2.rectangle(annotated, (x1, y1), (x2, y2), decision_color, box_thickness)

            label = f"{cls_name} {conf:.2f} ({region})"
            (tw, th), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, label_scale, 1
            )
            cv2.rectangle(
                annotated,
                (x1, y1 - th - baseline),
                (x1 + tw, y1),
                bg_color,
                cv2.FILLED,
            )
            cv2.putText(
                annotated,
                label,
                (x1, y1 - baseline),
                cv2.FONT_HERSHEY_SIMPLEX,
                label_scale,
                txt_color,
                1,
                cv2.LINE_AA,
            )

        # Draw overall decision
        main_scale = self.config["drawing"]["font_scale_main"]
        main_thick = self.config["drawing"]["font_thickness"]

        decision_txt = f"DECISION: {result.decision.decision.value}"
        severity_txt = f"SEVERITY: {result.decision.severity.value}"

        cv2.putText(
            annotated,
            decision_txt,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            main_scale,
            decision_color,
            main_thick,
        )
        cv2.putText(
            annotated,
            severity_txt,
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            main_scale,
            decision_color,
            main_thick,
        )

        return annotated
