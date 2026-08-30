from typing import Tuple


class CoordinateTransformer:
    """Handles mapping of bounding box coordinates from model-space to original-space."""

    def __init__(self, original_size: Tuple[int, int], model_size: Tuple[int, int]):
        """
        Args:
            original_size: (width, height) of the original camera frame.
            model_size: (width, height) of the model's input tensor.
        """
        self.orig_w, self.orig_h = original_size
        self.model_w, self.model_h = model_size

        # Calculate scaling factors
        # Assuming direct resize (no letterboxing) was used in preprocessing
        self.scale_x = self.orig_w / float(self.model_w) if self.model_w > 0 else 1.0
        self.scale_y = self.orig_h / float(self.model_h) if self.model_h > 0 else 1.0

    def transform(
        self, x1: float, y1: float, x2: float, y2: float
    ) -> Tuple[int, int, int, int]:
        """
        Transforms coordinates and clips them safely within the original frame boundaries.
        Args:
            x1, y1, x2, y2: Bounding box coordinates in model-space.
        Returns:
            (x1, y1, x2, y2): Bounding box coordinates in original camera-space, clipped.
        """
        # Scale
        tx1 = int(x1 * self.scale_x)
        ty1 = int(y1 * self.scale_y)
        tx2 = int(x2 * self.scale_x)
        ty2 = int(y2 * self.scale_y)

        # Clip safely
        tx1 = max(0, min(tx1, self.orig_w - 1))
        ty1 = max(0, min(ty1, self.orig_h - 1))
        tx2 = max(0, min(tx2, self.orig_w - 1))
        ty2 = max(0, min(ty2, self.orig_h - 1))

        # Ensure valid ordering
        if tx1 > tx2:
            tx1, tx2 = tx2, tx1
        if ty1 > ty2:
            ty1, ty2 = ty2, ty1

        # Ensure minimum size 1x1 while staying in bounds
        if tx1 == tx2:
            if tx2 < self.orig_w - 1:
                tx2 += 1
            else:
                tx1 -= 1
        if ty1 == ty2:
            if ty2 < self.orig_h - 1:
                ty2 += 1
            else:
                ty1 -= 1

        return tx1, ty1, tx2, ty2
