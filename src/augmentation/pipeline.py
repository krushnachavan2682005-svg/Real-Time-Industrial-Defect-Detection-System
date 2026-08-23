import logging
import random
from typing import List, Tuple, Any, Dict
import numpy as np

import albumentations as A
from src.augmentation.bbox_validation import validate_yolo_bboxes
from src.augmentation.transforms import build_train_transforms, load_augmentation_config

logger = logging.getLogger(__name__)


class AugmentationPipeline:
    """
    Wraps Albumentations transformations for YOLO format bounding boxes.
    """

    def __init__(self, config_path: str):
        """
        Initializes the pipeline with a YAML configuration.
        """
        self.config = load_augmentation_config(config_path)
        
        # Set seed for reproducibility if specified
        seed = self.config.get("seed", 42)
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        self.transform = build_train_transforms(self.config)
        logger.info(f"Initialized augmentation pipeline from {config_path}")

    def __call__(
        self, image: np.ndarray, bboxes: List[List[float]], class_labels: List[int]
    ) -> Tuple[np.ndarray, List[List[float]], List[int]]:
        """
        Applies augmentation to the image and bounding boxes.
        
        Args:
            image: numpy array (H, W, C)
            bboxes: List of YOLO formatted bounding boxes [[x_c, y_c, w, h], ...]
            class_labels: List of class integers
            
        Returns:
            Tuple of (augmented_image, valid_bboxes, valid_labels)
        """
        if len(bboxes) == 0:
            # Handle image without boxes
            transformed = self.transform(image=image, bboxes=[], class_labels=[])
            return transformed["image"], [], []

        try:
            transformed = self.transform(
                image=image, bboxes=bboxes, class_labels=class_labels
            )
            
            aug_image = transformed["image"]
            aug_bboxes = [list(box) for box in transformed["bboxes"]]
            aug_labels = transformed["class_labels"]
            
            valid_bboxes, valid_labels = validate_yolo_bboxes(aug_bboxes, aug_labels)
            
            return aug_image, valid_bboxes, valid_labels
            
        except Exception as e:
            logger.error(f"Augmentation failed: {e}. Returning original data.")
            # Safety fallback: return unaugmented
            return image, bboxes, class_labels
