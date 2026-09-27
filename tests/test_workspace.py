"""
Unit and integration tests for Cloud Workspace & Productivity System (Phase 9).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_project_crud_flow():
    # 1. Create project
    payload = {
        "name": "Phase 10 Hardening Project",
        "description": "Enterprise QA & Deployment project",
        "color": "#10b981"
    }
    res = client.post("/api/v1/projects", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    proj_id = data["data"]["id"]

    # 2. List projects
    res_list = client.get("/api/v1/projects")
    assert res_list.status_code == 200
    projects = res_list.json()["data"]
    assert any(p["id"] == proj_id for p in projects)

    # 3. Delete project
    res_del = client.delete(f"/api/v1/projects/{proj_id}")
    assert res_del.status_code == 200

def test_workspace_dashboard_overview():
    res = client.get("/api/v1/dashboard/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "overview" in data["data"]
    assert "storage" in data["data"]

def test_recycle_bin_operations():
    res = client.get("/api/v1/workspace/recycle-bin")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

def test_global_workspace_search():
    payload = {
        "query": "AetherMind",
        "entity_type": "all",
        "limit": 10
    }
    res = client.post("/api/v1/workspace/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "results" in data["data"]
