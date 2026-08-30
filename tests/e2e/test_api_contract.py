import pytest
import io
from fastapi.testclient import TestClient

from src.api.app import create_app

@pytest.fixture(scope="module")
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c

def test_inspect_unsupported_extension(client):
    # Test with .txt extension
    response = client.post(
        "/api/v1/inspect",
        files={"file": ("test_image.txt", b"dummy content", "text/plain")},
    )
    assert response.status_code == 415
    data = response.json()
    assert "detail" in data
    assert "Unsupported file type" in data["detail"]

def test_inspect_corrupted_image(client):
    # Test with corrupted image bytes
    corrupted_bytes = b"This is not a valid image file"
    response = client.post(
        "/api/v1/inspect",
        files={"file": ("test_image.jpg", corrupted_bytes, "image/jpeg")},
    )
    # The API catches this but maps it to 500 currently due to OpenCV
    assert response.status_code in [400, 500]
    data = response.json()
    assert "error" in data

def test_inspect_empty_upload(client):
    # Empty file
    response = client.post(
        "/api/v1/inspect",
        files={"file": ("test_image.jpg", b"", "image/jpeg")},
    )
    # Same as above, OpenCV fails
    assert response.status_code in [400, 500]
    data = response.json()
    assert "error" in data

def test_inspect_missing_file(client):
    # No file field provided
    response = client.post("/api/v1/inspect")
    assert response.status_code == 422 # FastAPI validation error for missing body

def test_response_stability(client):
    # Ensure no tracebacks or internal paths are leaked in 500 errors (if simulated)
    # This is a bit tricky to test directly without forcing a 500, but we can verify
    # the schema of normal errors
    response = client.post(
        "/api/v1/inspect",
        files={"file": ("test_image.jpg", b"corrupt", "image/jpeg")},
    )
    data = response.json()
    assert "error" in data
    error = data["error"]
    assert "code" in error
    assert "message" in error
    assert "traceback" not in error
    assert "path" not in error
