import pytest
from src.monitoring import metrics

def test_metrics_initialization():
    metrics._INITIALIZED = False # reset for testing
    metrics.init_metrics("test_ns", [0.1, 0.5])
    
    assert metrics._INITIALIZED is True
    assert metrics.http_requests_total is not None
    assert metrics.http_request_duration_seconds is not None
    assert metrics.inspections_total is not None
    
    # Try duplicate init
    metrics.init_metrics("another_ns", [1.0])
    assert metrics.http_requests_total._namespace == "test_ns" # shouldn't change
