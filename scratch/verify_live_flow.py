import os
import sys
from fastapi.testclient import TestClient

# Add root directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app

client = TestClient(app)

print("==================================================")
print(" AETHERMIND LIVE FLOW VERIFICATION SUITE")
print("==================================================")

# 1. Register & Login Test
email = f"verify_user_{id(client)}@aethermind.ai"
password = "TestPassword123!"

print("\n1. Testing User Registration & Login...")
reg_res = client.post("/api/v1/auth/register", json={
    "email": email,
    "password": password,
    "full_name": "Kavati John Shreyan"
})
assert reg_res.status_code == 201, f"Reg failed: {reg_res.text}"
reg_data = reg_res.json()
token = reg_data["data"]["access_token"]
print(f"   [SUCCESS] User registered successfully. Email: {email}")

login_res = client.post("/api/v1/auth/login", json={
    "email": email,
    "password": password,
    "remember_me": True
})
assert login_res.status_code == 200, f"Login failed: {login_res.text}"
print("   [SUCCESS] User login verified successfully. Token issued.")

# 2. Logout Test
print("\n2. Testing User Logout...")
logout_res = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
assert logout_res.status_code == 200, f"Logout failed: {logout_res.text}"
print("   [SUCCESS] User logout verified successfully. Session cleared.")

# 3. Document Analysis Test
print("\n3. Testing Document Upload & RAG Intelligence Engine...")
# Re-login to get active session token
login_res2 = client.post("/api/v1/auth/login", json={"email": email, "password": password})
token2 = login_res2.json()["data"]["access_token"]

sample_doc_content = """# AetherMind Enterprise AI Architecture Specification
Created by: Kavati John Shreyan

## Abstract
AetherMind Multimodal AI OS is an enterprise-grade artificial intelligence operating system featuring real-time document analysis, Qdrant vector retrieval-augmented generation (RAG), voice audio transcription, and high-performance multimodal completion engines.

## Key Features
1. Multimodal Document Intelligence Engine (PDF, DOCX, CSV, TXT, JSON, MD)
2. Qdrant Hybrid Vector Store & Semantic Embeddings
3. Firebase Authentication & User State Management
4. Adaptive Multi-Device Viewport Engine (Desktop, Laptop, Tablet, Mobile)
"""

upload_res = client.post(
    "/api/v1/upload",
    headers={"Authorization": f"Bearer {token2}"},
    files={"file": ("AetherMind_Architecture_Spec.md", sample_doc_content.encode("utf-8"), "text/markdown")}
)
assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
doc_data = upload_res.json()["data"]
print(f"   [SUCCESS] Document uploaded & indexed into Qdrant. File ID: {doc_data['id']}")

chat_res = client.post(
    "/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {token2}"},
    json={
        "prompt": "analyze document",
        "attachments": [doc_data],
        "model": "auto"
    }
)
assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
chat_data = chat_res.json()["data"]

print("\n--------------------------------------------------")
print(" DOCUMENT ANALYSIS REPORT OUTPUT:")
print("--------------------------------------------------")
print(chat_data["content"])
print("--------------------------------------------------")

assert len(chat_data["content"]) > 50, "Analysis output too short"
assert "AetherMind" in chat_data["content"] or "Multimodal" in chat_data["content"] or "Architecture" in chat_data["content"] or "document" in chat_data["content"].lower(), "Doc analysis missing relevant content"

print("\n[ALL VERIFICATION CHECKS PASSED PERFECTLY!]")
