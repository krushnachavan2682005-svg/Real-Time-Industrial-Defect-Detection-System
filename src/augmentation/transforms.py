import albumentations as A
import yaml
from typing import Any, Dict


def load_augmentation_config(config_path: str) -> Dict[str, Any]:
    """Loads augmentation configuration from a YAML file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def build_train_transforms(config: Dict[str, Any]) -> A.Compose:
    """
    Builds the Albumentations composition based on configuration.
    
    Args:
        config: The parsed YAML configuration.
        
    Returns:
        Albumentations Compose object.
    """
    transforms = []

    # Flips
    if config.get("horizontal_flip", {}).get("enabled", False):
        transforms.append(A.HorizontalFlip(p=config["horizontal_flip"].get("p", 0.5)))
        
    if config.get("vertical_flip", {}).get("enabled", False):
        transforms.append(A.VerticalFlip(p=config["vertical_flip"].get("p", 0.5)))

    # Geometric Shifts/Rotations
    if config.get("shift_scale_rotate", {}).get("enabled", False):
        cfg = config["shift_scale_rotate"]
        transforms.append(
            A.ShiftScaleRotate(
                shift_limit=cfg.get("shift_limit", 0.0625),
                scale_limit=cfg.get("scale_limit", 0.1),
                rotate_limit=cfg.get("rotate_limit", 15),
                p=cfg.get("p", 0.5),
            )
        )

    # Photometric Brightness/Contrast
    if config.get("random_brightness_contrast", {}).get("enabled", False):
        cfg = config["random_brightness_contrast"]
        transforms.append(
            A.RandomBrightnessContrast(
                brightness_limit=cfg.get("brightness_limit", 0.2),
                contrast_limit=cfg.get("contrast_limit", 0.2),
                p=cfg.get("p", 0.2),
            )
        )

    # Noise
    if config.get("gauss_noise", {}).get("enabled", False):
        cfg = config["gauss_noise"]
        var_limit = tuple(cfg.get("var_limit", (10.0, 50.0)))
        transforms.append(A.GaussNoise(var_limit=var_limit, p=cfg.get("p", 0.2)))

    # Setup bounding box parameters
    bbox_format = config.get("bbox_format", "yolo")
    min_visibility = config.get("min_visibility", 0.3)
    
    bbox_params = A.BboxParams(
        format=bbox_format,
        label_fields=["class_labels"],
        min_visibility=min_visibility
    )

    return A.Compose(transforms, bbox_params=bbox_params)
