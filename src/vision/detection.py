from dataclasses import dataclass


@dataclass
class Detection:
    """Structured representation of a single object detection."""

    class_id: int
    class_name: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    def to_dict(self) -> dict:
        """Serializes detection for potential JSON output or API responses."""
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": float(self.confidence),
            "bbox": [self.x1, self.y1, self.x2, self.y2],
        }
