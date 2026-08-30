import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.monitoring.service import MetricsService
from prometheus_client import generate_latest

def run_validation():
    print("=== Validating Monitoring & Metrics ===")
    
    # Initialize service
    service = MetricsService()
    if not service.enabled:
        print("Monitoring is disabled in config!")
        return

    print("1. Simulating API Requests...")
    service.record_http_request("POST", "/api/v1/inspect", 200, 0.045)
    service.record_http_request("GET", "/health", 200, 0.002)
    service.record_http_request("POST", "/api/v1/inspect", 500, 0.015)

    print("2. Simulating Inference and Pipeline Latency...")
    service.record_inference_latency(0.025)
    service.record_inference_latency(0.022)
    service.record_pipeline_latency(0.045)
    service.record_pipeline_latency(0.042)

    print("3. Simulating Decisions...")
    service.record_decision("PASS")
    service.record_decision("REJECT")
    service.record_decision("PASS")

    print("4. Simulating Defects...")
    service.record_defect("scratches")
    service.record_defect("scratches")
    service.record_defect("pitted_surface")

    print("5. Simulating PLC Commands...")
    service.record_plc_command("CONTINUE_CONVEYOR", True)
    service.record_plc_command("REJECT_PRODUCT", True)
    service.record_plc_command("REJECT_PRODUCT", False)

    print("6. Simulating Errors...")
    service.record_pipeline_error("inference")
    service.record_pipeline_error("api")

    print("7. Simulating Inspection Counter...")
    service.record_inspection(True)
    service.record_inspection(True)
    service.record_inspection(False)

    print("\n=== Dump of Prometheus Metrics ===")
    metrics_data = generate_latest().decode("utf-8")
    for line in metrics_data.split("\n"):
        if line and not line.startswith("#"):
            if any(k in line for k in ["industrial_defect_http", "industrial_defect_inspection", "industrial_defect_defect", "industrial_defect_model", "industrial_defect_plc", "industrial_defect_pipeline"]):
                print(line)

    print("\nValidation complete.")

if __name__ == "__main__":
    run_validation()
