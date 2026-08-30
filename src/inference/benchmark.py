import time
import numpy as np
import logging
import torch
from typing import Callable, Dict, Any, List

logger = logging.getLogger(__name__)

class BenchmarkRunner:
    """Handles latency benchmarking and FPS calculation for inference engines."""

    def __init__(self, warmup_iterations: int = 20, iterations: int = 100):
        self.warmup_iterations = warmup_iterations
        self.iterations = iterations

    def run_benchmark(self, name: str, inference_func: Callable[[], Any], sync_func: Callable[[], None] = lambda: None) -> Dict[str, Any]:
        """
        Runs benchmarking for a given inference function.
        
        Args:
            name: Human-readable name of the runtime (e.g., 'PyTorch CPU', 'ONNX CUDA')
            inference_func: A zero-argument function that runs a single inference pass.
            sync_func: An optional zero-argument function to synchronize device (e.g., torch.cuda.synchronize)
                       to ensure accurate timing when using async execution like CUDA.
        """
        logger.info(f"Starting benchmark for: {name}")
        
        # Warmup
        logger.debug(f"Running {self.warmup_iterations} warmup iterations...")
        for _ in range(self.warmup_iterations):
            inference_func()
            sync_func()
            
        latencies = []
        
        logger.debug(f"Running {self.iterations} benchmark iterations...")
        for _ in range(self.iterations):
            start_time = time.perf_counter()
            inference_func()
            sync_func()
            end_time = time.perf_counter()
            latencies.append((end_time - start_time) * 1000.0) # convert to ms
            
        latencies_arr = np.array(latencies)
        
        mean_latency = float(np.mean(latencies_arr))
        median_latency = float(np.median(latencies_arr))
        p95_latency = float(np.percentile(latencies_arr, 95))
        p99_latency = float(np.percentile(latencies_arr, 99))
        
        # FPS calculation based on mean latency
        fps = 1000.0 / mean_latency if mean_latency > 0 else 0.0
        
        result = {
            "runtime": name,
            "mean_ms": mean_latency,
            "median_ms": median_latency,
            "p95_ms": p95_latency,
            "p99_ms": p99_latency,
            "fps": fps
        }
        
        logger.info(f"Benchmark completed for {name}. Mean: {mean_latency:.2f}ms, FPS: {fps:.2f}")
        return result

def get_torch_sync_func() -> Callable[[], None]:
    """Returns the correct sync function depending on CUDA availability."""
    if torch.cuda.is_available():
        return torch.cuda.synchronize
    return lambda: None
