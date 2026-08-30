import pytest
import io
import cv2
import numpy as np
import threading
import time
from fastapi.testclient import TestClient

from src.api.app import create_app

@pytest.fixture(scope="module")
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c

@pytest.fixture
def valid_image_bytes():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    is_success, buffer = cv2.imencode(".jpg", img)
    if is_success:
        return io.BytesIO(buffer).read()
    return b""

def run_concurrent_requests(client, valid_image_bytes, num_requests):
    results = []
    
    def make_request():
        start = time.perf_counter()
        response = client.post(
            "/api/v1/inspect",
            files={"file": ("test_image.jpg", valid_image_bytes, "image/jpeg")},
        )
        end = time.perf_counter()
        results.append({
            "status": response.status_code,
            "latency": (end - start) * 1000
        })

    threads = []
    for _ in range(num_requests):
        t = threading.Thread(target=make_request)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    return results

def test_concurrent_requests_1(client, valid_image_bytes):
    results = run_concurrent_requests(client, valid_image_bytes, 1)
    assert len(results) == 1
    assert all(r["status"] == 200 for r in results)

def test_concurrent_requests_2(client, valid_image_bytes):
    results = run_concurrent_requests(client, valid_image_bytes, 2)
    assert len(results) == 2
    assert all(r["status"] == 200 for r in results)

def test_concurrent_requests_5(client, valid_image_bytes):
    results = run_concurrent_requests(client, valid_image_bytes, 5)
    assert len(results) == 5
    assert all(r["status"] == 200 for r in results)
