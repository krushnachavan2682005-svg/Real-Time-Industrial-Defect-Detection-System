import logging
from typing import Optional, Tuple, Union

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class CameraConfigError(Exception):
    pass


class CameraReadError(Exception):
    pass


class Camera:
    """Abstraction for a physical camera or video file source."""

    def __init__(self, source: Union[int, str]):
        """
        Initializes the camera/video source.
        Args:
            source: Integer camera ID (e.g., 0) or string path to a video file/image.
        """
        self.source = source
        self.cap: Optional[cv2.VideoCapture] = None
        self._is_image = isinstance(source, str) and source.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
        self._image_frame: Optional[np.ndarray] = None
        self.repeat_count = 1

    def open(self) -> bool:
        """Opens the video source."""
        if self._is_image and isinstance(self.source, str):
            self._image_frame = cv2.imread(self.source)
            if self._image_frame is None:
                raise CameraConfigError(f"Failed to load image from {self.source}")
            logger.info(f"Loaded image source: {self.source}")
            self._image_read_count = 0
            return True

        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise CameraConfigError(
                f"Failed to open camera/video source: {self.source}"
            )

        logger.info(f"Successfully opened source: {self.source}")
        return True

    def read(self) -> Optional[np.ndarray]:
        """
        Reads the next frame.
        Returns:
            np.ndarray (BGR frame) or None if the end of video is reached.
        Raises:
            CameraReadError if a live camera frame cannot be read.
        """
        if self._is_image:
            if self.repeat_count > 0 and self._image_read_count >= self.repeat_count:
                logger.info("End of image stream reached.")
                return None
            self._image_read_count += 1
            return self._image_frame.copy() if self._image_frame is not None else None

        if self.cap is None or not self.cap.isOpened():
            raise CameraConfigError("Camera is not opened. Call open() first.")

        ret, frame = self.cap.read()

        if not ret:
            # If it's a video file, it naturally ends.
            if isinstance(self.source, str):
                logger.info("End of video stream reached.")
                return None
            else:
                raise CameraReadError("Failed to grab frame from physical camera.")

        return frame

    def get_resolution(self) -> Tuple[int, int]:
        """Returns the current resolution (width, height)."""
        if self._is_image and self._image_frame is not None:
            h, w = self._image_frame.shape[:2]
            return w, h

        if self.cap is not None and self.cap.isOpened():
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        return 0, 0

    def get_fps(self) -> float:
        """Returns the source FPS if available."""
        if self._is_image:
            return 30.0  # arbitrary fallback

        if self.cap is not None and self.cap.isOpened():
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            return fps if fps > 0 else 30.0
        return 30.0

    def release(self) -> None:
        """Releases the camera resources safely."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self._image_frame = None
        logger.info(f"Released source: {self.source}")
