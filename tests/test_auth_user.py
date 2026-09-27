import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_user_registration():
    """Test user registration endpoint with unique email"""
    email = f"test_reg_{id(client)}@aethermind.ai"
    response = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "securepassword123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["email"] == email

def test_duplicate_user_registration_fails():
    """Test registering with an existing email returns 400 error"""
    email = f"duplicate_{id(client)}@aethermind.ai"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Initial User"
    })
    response = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Duplicate User"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_user_login():
    """Test user login with valid credentials and remember_me"""
    email = f"login_user_{id(client)}@aethermind.ai"
    password = "mysecretpassword"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Login User"
    })

    # Perform Login
    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password,
        "remember_me": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]

def test_invalid_login_credentials_fail():
    """Test login with wrong password returns 401 error"""
    email = f"invalid_login_{id(client)}@aethermind.ai"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "correctpassword",
        "full_name": "Invalid Login User"
    })

    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_clerk_auth_integration():
    """Test Clerk authentication endpoint and user provision"""
    response = client.post("/api/v1/auth/clerk", json={
        "token": "clerk_mock_test_token_123",
        "email": f"clerk_{id(client)}@aethermind.ai",
        "full_name": "Clerk Test User",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=clerk"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]

def test_google_oauth_login():
    """Test Google OAuth login endpoint"""
    response = client.post("/api/v1/auth/oauth/google", json={
        "provider": "google",
        "id_token": "mock_google_id_token",
        "email": f"google_{id(client)}@aethermind.ai",
        "full_name": "Google Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]

def test_github_oauth_login():
    """Test GitHub OAuth login endpoint"""
    response = client.post("/api/v1/auth/oauth/github", json={
        "provider": "github",
        "id_token": "mock_github_id_token",
        "email": f"github_{id(client)}@aethermind.ai",
        "full_name": "GitHub Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]

def test_microsoft_oauth_login():
    """Test Microsoft OAuth login endpoint"""
    response = client.post("/api/v1/auth/oauth/microsoft", json={
        "provider": "microsoft",
        "id_token": "mock_microsoft_id_token",
        "email": f"microsoft_{id(client)}@aethermind.ai",
        "full_name": "Microsoft Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]

def test_protected_profile_route_without_token():
    """Test accessing protected route without token returns 401"""
    fresh_client = TestClient(app)
    response = fresh_client.get("/api/v1/user/me")
    assert response.status_code == 401


def test_protected_profile_route_with_valid_token():
    """Test accessing profile with valid token"""
    email = f"profile_{id(client)}@aethermind.ai"
    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "profilepassword",
        "full_name": "Profile User"
    })
    token = reg.json()["data"]["access_token"]

    response = client.get("/api/v1/user/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == email

def test_profile_update():
    """Test updating full name and avatar via PATCH /api/v1/user/me"""
    email = f"update_prof_{id(client)}@aethermind.ai"
    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Old Name"
    })
    token = reg.json()["data"]["access_token"]

    response = client.patch(
        "/api/v1/user/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "New Updated Name", "avatar_url": "https://example.com/new_avatar.png"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["full_name"] == "New Updated Name"
    assert data["avatar_url"] == "https://example.com/new_avatar.png"

def test_user_settings_retrieval_and_update():
    """Test retrieving and updating user settings & preferences"""
    email = f"settings_{id(client)}@aethermind.ai"
    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Settings User"
    })
    token = reg.json()["data"]["access_token"]

    # Get settings
    get_res = client.get("/api/v1/user/settings", headers={"Authorization": f"Bearer {token}"})
    assert get_res.status_code == 200

    # Update settings
    put_res = client.put(
        "/api/v1/user/settings",
        headers={"Authorization": f"Bearer {token}"},
        json={"theme": "dark", "default_model": "claude-3-5-sonnet", "custom_instructions": "Be ultra concise"}
    )
    assert put_res.status_code == 200
    updated = put_res.json()["data"]
    assert updated["default_model"] == "claude-3-5-sonnet"
    assert updated["custom_instructions"] == "Be ultra concise"

def test_forgot_password_and_reset_flow():
    """Test forgot password token generation and password reset confirmation"""
    email = f"reset_{id(client)}@aethermind.ai"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "oldpassword123",
        "full_name": "Reset User"
    })

    # Forgot password
    forgot_res = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert forgot_res.status_code == 200
    reset_token = forgot_res.json()["data"]["reset_token"]

    # Reset password
    reset_res = client.post("/api/v1/auth/reset-password", json={
        "token": reset_token,
        "new_password": "brandnewpassword123"
    })
    assert reset_res.status_code == 200

    # Login with new password
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": "brandnewpassword123"})
    assert login_res.status_code == 200

def test_logout():
    """Test logout endpoint revokes token and session"""
    email = f"logout_{id(client)}@aethermind.ai"
    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Logout User"
    })
    token = reg.json()["data"]["access_token"]

    logout_res = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200
    assert logout_res.json()["data"]["status"] == "logged_out"
