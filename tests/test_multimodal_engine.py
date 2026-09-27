"""
Unit and integration tests for Multimodal AI Engine (Phase 7).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_completion_endpoint():
    payload = {
        "prompt": "Hello AetherMind AI!",
        "model": "gemini-2.5-flash",
        "attachment_ids": []
    }
    response = client.post("/api/v1/chat/completions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "content" in data["data"]
    assert data["data"]["chat_id"] is not None

def test_image_generation_endpoint():
    payload = {
        "prompt": "Futuristic neon city at night",
        "style": "photorealistic",
        "aspect_ratio": "16:9",
        "quality": "hd"
    }
    response = client.post("/api/v1/image/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["image_url"] is not None
    assert data["data"]["prompt"] == payload["prompt"]

def test_vision_analysis_mock():
    # Pass image file bytes via multipart form data
    files = {"file": ("sample.png", b"fake_image_binary_data", "image/png")}
    data = {"prompt": "Describe this image"}
    response = client.post("/api/v1/image/analyze", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert "analysis" in res_data["data"]

def test_list_conversations():
    response = client.get("/api/v1/chat/conversations")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
