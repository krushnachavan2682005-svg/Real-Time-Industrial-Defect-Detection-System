import pytest
import numpy as np
from src.inference.benchmark import BenchmarkRunner

def test_benchmark_runner_latency_calc():
    runner = BenchmarkRunner(warmup_iterations=2, iterations=10)
    
    # Mock inference function that just sleeps for 10ms
    def mock_inference():
        import time
        time.sleep(0.01)
        
    result = runner.run_benchmark("MockRuntime", mock_inference)
    
    assert result['runtime'] == "MockRuntime"
    assert "mean_ms" in result
    assert "median_ms" in result
    assert "p95_ms" in result
    assert "p99_ms" in result
    assert "fps" in result
    
    # Assert values are somewhat reasonable (around 10ms)
    assert 5.0 < result['mean_ms'] < 30.0
    assert result['fps'] > 0
    
def test_benchmark_sync_func():
    # Test that it calls sync func
    sync_called = False
    def mock_sync():
        nonlocal sync_called
        sync_called = True
        
    runner = BenchmarkRunner(warmup_iterations=1, iterations=1)
    runner.run_benchmark("SyncTest", lambda: None, sync_func=mock_sync)
    
    assert sync_called
