from typing import List

import cv2
import numpy as np

from src.vision.detection import Detection


class Visualizer:
    """Handles drawing detections and performance metrics on a frame."""

    # Pre-define some colors for different classes
    COLORS = [
        (255, 56, 56),
        (255, 157, 151),
        (255, 112, 31),
        (255, 178, 29),
        (207, 210, 49),
        (72, 249, 10),
        (146, 204, 23),
        (61, 219, 134),
        (26, 147, 52),
        (0, 212, 187),
        (44, 153, 168),
        (0, 194, 255),
    ]

    def __init__(self, display_metrics: bool = True):
        self.display_metrics = display_metrics

    def _get_color(self, class_id: int) -> tuple:
        """Returns a consistent color for a given class ID."""
        return self.COLORS[class_id % len(self.COLORS)]

    def draw_detections(
        self, frame: np.ndarray, detections: List[Detection]
    ) -> np.ndarray:
        """
        Draws bounding boxes and labels on the frame.
        Args:
            frame: Original BGR camera frame.
            detections: List of Detection objects (coordinates must be in original-space).
        Returns:
            Annotated frame.
        """
        annotated_frame = frame.copy()

        for det in detections:
            color = self._get_color(det.class_id)

            # Draw bounding box
            cv2.rectangle(
                annotated_frame, (det.x1, det.y1), (det.x2, det.y2), color, thickness=2
            )

            # Draw label
            label = f"{det.class_name.upper()} {det.confidence:.2f}"

            # Add text background for readability
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )

            cv2.rectangle(
                annotated_frame,
                (det.x1, det.y1 - text_height - baseline),
                (det.x1 + text_width, det.y1),
                color,
                thickness=cv2.FILLED,
            )

            cv2.putText(
                annotated_frame,
                label,
                (det.x1, det.y1 - baseline),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

        return annotated_frame

    def draw_metrics(
        self, frame: np.ndarray, inference_ms: float, e2e_ms: float, fps: float
    ) -> np.ndarray:
        """Draws performance metrics in the top left corner."""
        if not self.display_metrics:
            return frame

        annotated = frame.copy()

        lines = [
            f"FPS: {fps:.1f}",
            f"Inference: {inference_ms:.1f} ms",
            f"End-to-End: {e2e_ms:.1f} ms",
        ]

        y_offset = 30
        for line in lines:
            # Shadow
            cv2.putText(
                annotated,
                line,
                (12, y_offset + 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 0),
                2,
                cv2.LINE_AA,
            )
            # Text
            cv2.putText(
                annotated,
                line,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            y_offset += 30

        return annotated
