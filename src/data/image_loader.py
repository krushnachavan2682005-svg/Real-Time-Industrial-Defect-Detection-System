from pathlib import Path
from typing import Union

import cv2
import numpy as np

from src.core.exceptions import DataError
from src.core.logging import configure_logging

logger = configure_logging(name=__name__)


def load_image(
    image_path: Union[str, Path], as_rgb: bool = False, as_gray: bool = False
) -> np.ndarray:
    """
    Safely load an image from the given path.
    By default, loads the image unchanged (preserving original channels),
    since the NEU dataset contains grayscale images and we do not want to
    silently convert them to RGB.

    Args:
        image_path: Path to the image file.
        as_rgb: If True, force conversion of the image to RGB.
        as_gray: If True, force loading the image as grayscale.

    Returns:
        numpy.ndarray representing the loaded image.

    Raises:
        DataError: If the file does not exist, cannot be read, or is corrupted.
    """
    path_obj = Path(image_path)

    if not path_obj.exists():
        logger.error(f"Image not found at path: {path_obj}")
        raise DataError(f"Image not found: {path_obj}")

    if not path_obj.is_file():
        logger.error(f"Path is not a file: {path_obj}")
        raise DataError(f"Path is not a file: {path_obj}")

    # Determine OpenCV flags
    flags = cv2.IMREAD_UNCHANGED
    if as_gray:
        flags = cv2.IMREAD_GRAYSCALE
    elif as_rgb:
        flags = cv2.IMREAD_COLOR

    # Load image
    image = cv2.imread(str(path_obj), flags)

    if image is None:
        logger.error(f"Failed to read image or image is corrupted: {path_obj}")
        raise DataError(f"Failed to read image or image is corrupted: {path_obj}")

    # OpenCV loads color images in BGR format by default when using IMREAD_COLOR
    # If the user explicitly requested RGB, we must convert from BGR to RGB
    if as_rgb and len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image
