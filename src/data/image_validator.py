"""
Image Validator module.
Validates the structural and format integrity of a single image file.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from src.core.exceptions import DataError
from src.core.logging import configure_logging
from src.data.image_loader import load_image

logger = configure_logging(name=__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


@dataclass
class ImageValidationResult:
    """Represents the outcome of validating a single image."""
    is_valid: bool
    file_path: str
    width: Optional[int] = None
    height: Optional[int] = None
    channels: Optional[int] = None
    file_size_bytes: Optional[int] = None
    error_reason: Optional[str] = None


def validate_image(image_path: Union[str, Path]) -> ImageValidationResult:
    """
    Validates a single image file.

    Checks performed:
    - File existence and is_file
    - Valid extension against supported types
    - File size > 0
    - Readable and uncorrupted (via image_loader)
    - Valid dimensions (width and height > 0)

    Args:
        image_path: Path to the image file to validate.

    Returns:
        ImageValidationResult containing validation status and metadata.
    """
    path_obj = Path(image_path)

    # 1. Check existence
    if not path_obj.exists() or not path_obj.is_file():
        return ImageValidationResult(
            is_valid=False,
            file_path=str(path_obj),
            error_reason="File does not exist or is not a regular file.",
        )

    # 2. Check extension
    if path_obj.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return ImageValidationResult(
            is_valid=False,
            file_path=str(path_obj),
            error_reason=f"Unsupported file extension: {path_obj.suffix}",
        )

    # 3. Check file size (not empty)
    try:
        file_size = path_obj.stat().st_size
        if file_size == 0:
            return ImageValidationResult(
                is_valid=False,
                file_path=str(path_obj),
                file_size_bytes=0,
                error_reason="File is empty (0 bytes).",
            )
    except OSError as e:
        return ImageValidationResult(
            is_valid=False,
            file_path=str(path_obj),
            error_reason=f"OS Error while reading file stats: {e}",
        )

    # 4. Attempt to load the image
    try:
        image = load_image(path_obj)
    except DataError as e:
        return ImageValidationResult(
            is_valid=False,
            file_path=str(path_obj),
            file_size_bytes=file_size,
            error_reason=f"Corrupted or unreadable image: {str(e)}",
        )

    # 5. Extract dimensions and structure
    if image.size == 0:
        return ImageValidationResult(
            is_valid=False,
            file_path=str(path_obj),
            file_size_bytes=file_size,
            error_reason="Image array has 0 size.",
        )

    shape = image.shape
    height = shape[0]
    width = shape[1]
    channels = shape[2] if len(shape) > 2 else 1

    if height == 0 or width == 0:
        return ImageValidationResult(
            is_valid=False,
            file_path=str(path_obj),
            file_size_bytes=file_size,
            width=width,
            height=height,
            channels=channels,
            error_reason="Invalid image dimensions (0 width or height).",
        )

    # All checks passed
    return ImageValidationResult(
        is_valid=True,
        file_path=str(path_obj),
        width=width,
        height=height,
        channels=channels,
        file_size_bytes=file_size,
    )
