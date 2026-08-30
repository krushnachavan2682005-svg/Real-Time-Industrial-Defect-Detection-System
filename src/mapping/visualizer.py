import cv2
import numpy as np
import yaml

from src.core.exceptions import MappingError
from src.mapping.models import InspectionResult


class Visualizer:
    def __init__(self, config_path: str = "configs/mapping/visualization.yaml"):
        self.config = self._load_config(config_path)
        self.style = self.config.get("style", {})
        self.colors = self.config.get("colors", {})

    def _load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception:
            # Fallback configuration
            return {
                "style": {
                    "box_thickness": 2,
                    "font_scale": 0.6,
                    "font_thickness": 1,
                    "text_padding": 5,
                    "panel_alpha": 0.6,
                },
                "colors": {
                    "PASS": [0, 255, 0],
                    "REVIEW": [0, 255, 255],
                    "REJECT": [0, 0, 255],
                    "DEFAULT_BOX": [255, 255, 0],
                    "TEXT": [255, 255, 255],
                    "TEXT_BACKGROUND": [0, 0, 0],
                },
            }

    def render(self, frame: np.ndarray, result: InspectionResult) -> np.ndarray:
        """
        Renders the inspection result onto a copy of the frame.
        """
        if not isinstance(frame, np.ndarray) or frame.size == 0:
            raise MappingError("Invalid frame provided for visualization.")

        annotated_frame = frame.copy()

        box_thickness = self.style.get("box_thickness", 2)
        font_scale = self.style.get("font_scale", 0.6)
        font_thickness = self.style.get("font_thickness", 1)

        decision_val = result.decision.decision.value
        main_color = self.colors.get(
            decision_val, self.colors.get("DEFAULT_BOX", [255, 255, 0])
        )

        # Draw defects
        for defect in result.defects:
            orig = defect.original_detection
            bbox = orig.get("bbox", [0, 0, 0, 0])
            x1, y1, x2, y2 = bbox

            # Draw bounding box
            cv2.rectangle(
                annotated_frame, (x1, y1), (x2, y2), main_color, box_thickness
            )

            # Draw label
            label = (
                f"{orig.get('class_name', 'unknown')} {orig.get('confidence', 0.0):.2f}"
            )
            (text_w, text_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness
            )

            # Draw text background
            cv2.rectangle(
                annotated_frame,
                (x1, y1 - text_h - 10),
                (x1 + text_w, y1),
                self.colors.get("TEXT_BACKGROUND", [0, 0, 0]),
                -1,
            )
            cv2.putText(
                annotated_frame,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                self.colors.get("TEXT", [255, 255, 255]),
                font_thickness,
            )

        # Draw summary panel
        panel_text = [
            f"DECISION: {decision_val}",
            f"SEVERITY: {result.decision.severity.value}",
            f"DEFECTS: {result.defect_count}",
        ]

        y_offset = 30
        for text in panel_text:
            cv2.putText(
                annotated_frame,
                text,
                (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                main_color,
                2,
            )
            y_offset += 30

        return annotated_frame
