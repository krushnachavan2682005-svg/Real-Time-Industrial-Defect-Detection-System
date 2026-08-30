import collections
import time
from typing import Deque


class PerformanceMonitor:
    """Tracks latency and calculates FPS for real-time video processing."""

    def __init__(self, warmup_frames: int = 20, history_size: int = 30):
        self.warmup_frames = warmup_frames
        self.history_size = history_size
        self.frame_count = 0

        self.inference_latencies: Deque[float] = collections.deque(maxlen=history_size)
        self.e2e_latencies: Deque[float] = collections.deque(maxlen=history_size)

        self._e2e_start_time = 0.0
        self._inf_start_time = 0.0

    def start_frame(self):
        """Marks the start of the entire processing pipeline for a frame."""
        self._e2e_start_time = time.perf_counter()

    def start_inference(self):
        """Marks the start of the ONNX inference."""
        self._inf_start_time = time.perf_counter()

    def end_inference(self):
        """Marks the end of ONNX inference and records latency."""
        latency = (time.perf_counter() - self._inf_start_time) * 1000.0
        if self.frame_count >= self.warmup_frames:
            self.inference_latencies.append(latency)

    def end_frame(self):
        """Marks the end of the full pipeline for a frame and records end-to-end latency."""
        latency = (time.perf_counter() - self._e2e_start_time) * 1000.0
        if self.frame_count >= self.warmup_frames:
            self.e2e_latencies.append(latency)

        self.frame_count += 1

    def get_avg_inference_latency(self) -> float:
        if not self.inference_latencies:
            return 0.0
        return sum(self.inference_latencies) / len(self.inference_latencies)

    def get_avg_e2e_latency(self) -> float:
        if not self.e2e_latencies:
            return 0.0
        return sum(self.e2e_latencies) / len(self.e2e_latencies)

    def get_fps(self) -> float:
        avg_e2e = self.get_avg_e2e_latency()
        if avg_e2e > 0:
            return 1000.0 / avg_e2e
        return 0.0
