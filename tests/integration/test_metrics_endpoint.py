import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "industrial_defect_http_requests" in response.text or "python_info" in response.text
