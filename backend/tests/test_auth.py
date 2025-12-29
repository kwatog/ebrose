import pytest
from fastapi.testclient import TestClient


def test_login_success(client, admin_user, db_session):
    """Test successful login."""
    response = client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["user"]["username"] == "testadmin"
    assert data["user"]["role"] == "Admin"
    assert "access_token" in response.cookies


def test_login_invalid_credentials(client, admin_user):
    """Test login with invalid password."""
    response = client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/user-groups")
    assert response.status_code == 401


def test_protected_endpoint_with_token(client, admin_user, admin_token):
    """Test accessing protected endpoint with valid token."""
    response = client.get(
        "/user-groups",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200


def test_token_refresh(client, admin_user, admin_token):
    """Test token refresh endpoint."""
    response = client.post(
        "/auth/refresh",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies


def test_logout(client, admin_user, admin_token):
    """Test logout endpoint."""
    response = client.post(
        "/auth/logout",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    # Token should be cleared (either empty or not present)
    token = response.cookies.get("access_token")
    assert token is None or token == ""
