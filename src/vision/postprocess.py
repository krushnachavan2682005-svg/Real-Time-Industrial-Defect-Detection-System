from typing import Dict, List

import cv2
import numpy as np

from src.vision.detection import Detection


class Postprocessor:
    """Handles parsing YOLOv8 ONNX raw outputs and applying NMS."""

    def __init__(
        self,
        class_map: Dict[int, str],
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.50,
    ):
        """
        Args:
            class_map: Dictionary mapping class IDs to class names.
            conf_threshold: Minimum confidence threshold.
            iou_threshold: NMS IoU threshold.
        """
        self.class_map = class_map
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

    def process(self, raw_output: np.ndarray) -> List[Detection]:
        """
        Processes raw YOLOv8 ONNX output into Detection objects.

        Args:
            raw_output: NumPy array of shape [1, 4+num_classes, num_anchors]
        Returns:
            List of Detection objects (in model-space coordinates).
        """
        # YOLOv8 export shape is usually [batch, num_features, num_anchors]
        # Example: [1, 10, 1029] for 6 classes

        # Remove batch dim and transpose to [num_anchors, num_features]
        # -> shape: [1029, 10]
        preds = raw_output[0].T

        boxes = []
        scores = []
        class_ids = []

        for pred in preds:
            # pred is [cx, cy, w, h, class0_score, class1_score, ...]
            class_scores = pred[4:]
            class_id = np.argmax(class_scores)
            confidence = class_scores[class_id]

            if confidence > self.conf_threshold:
                cx, cy, w, h = pred[0:4]

                # Convert to top-left x, y, width, height for cv2 NMS
                x1 = cx - w / 2
                y1 = cy - h / 2

                boxes.append([int(x1), int(y1), int(w), int(h)])
                scores.append(float(confidence))
                class_ids.append(class_id)

        if not boxes:
            return []

        # Apply NMS
        # cv2.dnn.NMSBoxes expects boxes as [x, y, w, h] and returns indices
        raw_indices = cv2.dnn.NMSBoxes(
            boxes, scores, self.conf_threshold, self.iou_threshold
        )
        indices = np.array(raw_indices)

        detections = []
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                confidence = scores[i]
                class_id = class_ids[i]
                class_name = self.class_map.get(class_id, f"class_{class_id}")

                detections.append(
                    Detection(
                        class_id=class_id,
                        class_name=class_name,
                        confidence=confidence,
                        x1=x,
                        y1=y,
                        x2=x + w,
                        y2=y + h,
                    )
                )

        return detections
