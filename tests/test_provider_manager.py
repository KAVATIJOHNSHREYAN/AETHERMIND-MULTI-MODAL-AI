import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.providers.registry import provider_registry
from app.providers.manager import ai_provider_manager
from app.security.key_manager import APIKeyManager

client = TestClient(app)

def test_provider_registry_contains_13_providers():
    providers = provider_registry.list_all_providers()
    assert len(providers) == 13
    names = [p["name"] for p in providers]
    assert "google_gemini" in names
    assert "openai" in names
    assert "anthropic_claude" in names
    assert "groq" in names
    assert "deepseek" in names
    assert "ollama" in names
    assert "apiless" in names

def test_key_encryption_and_decryption():
    raw_key = "sk-test-secret-key-12345"
    encrypted = APIKeyManager.encrypt_key(raw_key)
    assert encrypted != raw_key
    decrypted = APIKeyManager.decrypt_key(encrypted)
    assert decrypted == raw_key

def test_key_masking():
    masked = APIKeyManager.mask_key("sk-proj-1234567890abcdef")
    assert masked.startswith("sk-p")
    assert masked.endswith("cdef")
    assert "..." in masked

def test_provider_resolution():
    gemini_p = provider_registry.resolve_provider_for_model("gemini-2.5-flash")
    assert gemini_p is not None
    assert gemini_p.provider_name == "google_gemini"

    openai_p = provider_registry.resolve_provider_for_model("gpt-4o")
    assert openai_p is not None
    assert openai_p.provider_name == "openai"

def test_ai_provider_manager_generate():
    res = asyncio.run(ai_provider_manager.generate(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": "Hello AetherMind"}]
    ))
    assert isinstance(res, str)
    assert len(res) > 0

def test_list_providers_endpoint():
    response = client.get("/api/v1/providers")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 13

def test_test_provider_endpoint():
    response = client.post("/api/v1/providers/test", json={
        "provider_name": "google_gemini",
        "api_key": "AIzaSyTestKey123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["provider"] == "google_gemini"

def test_dispatch_ai_endpoint():
    response = client.post("/api/v1/providers/dispatch", json={
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Test dispatch"}]
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data["data"]
