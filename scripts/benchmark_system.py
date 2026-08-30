import argparse
import time
import json
import os
import datetime
import numpy as np
import cv2
import platform
import sys
from fastapi.testclient import TestClient

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.app import create_app

def generate_test_image(path):
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (150, 150), (255, 255, 255), -1)
    cv2.imwrite(path, img)

def run_benchmark(image_path, warmup, iterations):
    app = create_app()
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    with TestClient(app) as client:
        print(f"Starting warmup ({warmup} iterations)...")
        for _ in range(warmup):
            client.post(
                "/api/v1/inspect",
                files={"file": ("test_image.jpg", image_bytes, "image/jpeg")},
            )
            
        print(f"Starting measurement ({iterations} iterations)...")
        latencies = []
        
        start_total = time.perf_counter()
        for _ in range(iterations):
            start_req = time.perf_counter()
            resp = client.post(
                "/api/v1/inspect",
                files={"file": ("test_image.jpg", image_bytes, "image/jpeg")},
            )
            end_req = time.perf_counter()
            
            if resp.status_code == 200:
                latencies.append((end_req - start_req) * 1000)
        end_total = time.perf_counter()
    
    if not latencies:
        print("All requests failed!")
        return None
        
    total_time = end_total - start_total
    throughput = len(latencies) / total_time
    
    results = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "device": "CPU"
        },
        "benchmark": {
            "warmup_iterations": warmup,
            "measured_iterations": iterations
        },
        "latency_ms": {
            "mean": float(np.mean(latencies)),
            "median": float(np.median(latencies)),
            "p95": float(np.percentile(latencies, 95)),
            "p99": float(np.percentile(latencies, 99)),
            "min": float(np.min(latencies)),
            "max": float(np.max(latencies))
        },
        "throughput": {
            "requests_per_second": throughput
        }
    }
    return results

def main():
    parser = argparse.ArgumentParser(description="System Benchmark")
    parser.add_argument("--image", type=str, default="test_image.jpg", help="Path to test image")
    parser.add_argument("--warmup", type=int, default=10, help="Warmup iterations")
    parser.add_argument("--iterations", type=int, default=100, help="Measured iterations")
    parser.add_argument("--output", type=str, default="reports/benchmarks/system_benchmark.json")
    args = parser.parse_args()

    image_path = args.image
    remove_image = False
    if not os.path.exists(image_path):
        print(f"Image {image_path} not found. Generating dummy image...")
        generate_test_image(image_path)
        remove_image = True

    results = run_benchmark(image_path, args.warmup, args.iterations)
    
    if remove_image and os.path.exists(image_path):
        os.remove(image_path)
        
    if results:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Benchmark completed. Results saved to {args.output}")
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
