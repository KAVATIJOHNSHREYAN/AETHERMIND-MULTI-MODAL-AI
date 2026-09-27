from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"

def test_liveness_endpoint():
    response = client.get("/api/v1/health/liveness")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["liveness"] is True

def test_readiness_endpoint():
    response = client.get("/api/v1/health/readiness")
    assert response.status_code == 200
    data = response.json()
    assert "postgresql" in data["data"]
    assert "redis" in data["data"]

def test_system_info_endpoint():
    response = client.get("/api/v1/health/system")
    assert response.status_code == 200
    data = response.json()
    assert "python_version" in data["data"]
