import pytest
from src.monitoring.service import MetricsService
from src.monitoring import metrics

def test_metrics_service_methods(monkeypatch):
    # Mock to avoid trying to load config file if not in right dir
    monkeypatch.setattr("src.monitoring.service.MetricsService._load_config", lambda self: {"monitoring": {"enabled": True}})
    metrics._INITIALIZED = False # reset
    service = MetricsService(config_path="fake.yaml")
    
    assert service.enabled is True
    
    # Verify methods don't raise exceptions
    service.record_http_request("GET", "/test", 200, 0.1)
    service.record_inspection(True)
    service.record_decision("PASS")
    service.record_inference_latency(0.05)
    service.record_pipeline_latency(0.1)
    service.record_defect("scratches")
    service.record_plc_command("PASS_CMD", True)
    service.record_pipeline_error("api")
