"""
Unit and integration tests for Memory Engine and Knowledge System (Phase 8).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_knowledge_collection_lifecycle():
    # 1. Create collection
    create_payload = {
        "name": "Test Engineering Collection",
        "description": "System specifications and documentation",
        "tags": ["testing", "specs"]
    }
    res = client.post("/api/v1/knowledge/collections", json=create_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    col_id = data["data"]["id"]

    # 2. List collections
    res_list = client.get("/api/v1/knowledge/collections")
    assert res_list.status_code == 200
    cols = res_list.json()["data"]
    assert any(c["id"] == col_id for c in cols)

def test_memory_storage_and_retrieval():
    # 1. Add memory
    mem_payload = {
        "memory_type": "preference",
        "memory_key": "user_theme_preference",
        "memory_value": "Dark Mode Cyberpunk Theme",
        "category": "ui_settings"
    }
    res = client.post("/api/v1/memory", json=mem_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    mem_id = data["data"]["id"]

    # 2. List memories
    res_list = client.get("/api/v1/memory")
    assert res_list.status_code == 200
    memories = res_list.json()["data"]
    assert any(m["id"] == mem_id for m in memories)

    # 3. Delete memory
    res_del = client.delete(f"/api/v1/memory/{mem_id}")
    assert res_del.status_code == 200

def test_hybrid_search_endpoint():
    search_payload = {
        "query": "Dark Mode preference",
        "search_type": "hybrid",
        "limit": 5
    }
    res = client.post("/api/v1/search", json=search_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "results" in data["data"]
