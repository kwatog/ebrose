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


def test_password_change_success(client, regular_user, user_token):
    """Test successful password change."""
    response = client.post(
        "/auth/password",
        json={
            "current_password": "testpass123",
            "new_password": "NewPass123!"
        },
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"


def test_password_change_wrong_current_password(client, regular_user, user_token):
    """Test password change with wrong current password."""
    response = client.post(
        "/auth/password",
        json={
            "current_password": "wrongpassword",
            "new_password": "NewPass123!"
        },
        cookies={"access_token": user_token}
    )
    assert response.status_code == 401
    assert "Current password is incorrect" in response.json()["detail"]


def test_password_change_weak_password(client, regular_user, user_token):
    """Test password change with weak password that doesn't meet policy."""
    response = client.post(
        "/auth/password",
        json={
            "current_password": "testpass123",
            "new_password": "weak"
        },
        cookies={"access_token": user_token}
    )
    assert response.status_code == 400
    assert "at least 8 characters" in response.json()["detail"].lower() or \
           "uppercase" in response.json()["detail"].lower() or \
           "digit" in response.json()["detail"].lower()


def test_update_me(client, regular_user, user_token):
    """Test updating user profile."""
    response = client.put(
        "/auth/me",
        json={
            "full_name": "Updated Name",
            "department": "New Department"
        },
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["department"] == "New Department"


def test_update_me_partial(client, regular_user, user_token):
    """Test partial update of user profile."""
    response = client.put(
        "/auth/me",
        json={"full_name": "Only Name Updated"},
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Only Name Updated"
    # Department should remain unchanged (None in request)
    assert response.json()["department"] == regular_user.department


def test_password_policy_enforcement_on_register(client, admin_user, admin_token, db_session):
    """Test that password policy is enforced during user registration."""
    from app.models import User
    
    # Try to register with weak password
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "new@test.com",
            "full_name": "New User",
            "password": "weak",
            "role": "User"
        },
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 400
    assert "at least 8 characters" in response.json()["detail"].lower() or \
           "uppercase" in response.json()["detail"].lower() or \
           "digit" in response.json()["detail"].lower() or \
           "special" in response.json()["detail"].lower()
    
    # Verify user was not created
    user = db_session.query(User).filter(User.username == "newuser").first()
    assert user is None


def test_password_change_works_with_new_password(client, regular_user, user_token):
    """Test that password change works and new password can be used for login."""
    from app.auth import get_password_hash

    new_password = "SecurePass456!"
    current_hashed = regular_user.hashed_password

    # Change password
    response = client.post(
        "/auth/password",
        json={
            "current_password": "testpass123",
            "new_password": new_password
        },
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"

    # Verify old password no longer works
    login_response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    assert login_response.status_code == 401

    # Verify new password works
    login_response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": new_password}
    )
    assert login_response.status_code == 200


def test_password_change_rejects_missing_uppercase(client, regular_user, user_token):
    """Test password change rejects password without uppercase."""
    response = client.post(
        "/auth/password",
        json={
            "current_password": "testpass123",
            "new_password": "lowercase123!"
        },
        cookies={"access_token": user_token}
    )
    assert response.status_code == 400
    assert "uppercase" in response.json()["detail"].lower()


def test_password_change_rejects_missing_lowercase(client, regular_user, user_token):
    """Test password change rejects password without lowercase."""
    response = client.post(
        "/auth/password",
        json={
            "current_password": "testpass123",
            "new_password": "UPPERCASE123!"
        },
        cookies={"access_token": user_token}
    )
    assert response.status_code == 400
    assert "lowercase" in response.json()["detail"].lower()


def test_password_change_rejects_missing_digit(client, regular_user, user_token):
    """Test password change rejects password without digit."""
    response = client.post(
        "/auth/password",
        json={
            "current_password": "testpass123",
            "new_password": "NoDigitsHere!"
        },
        cookies={"access_token": user_token}
    )
    assert response.status_code == 400
    assert "digit" in response.json()["detail"].lower()


def test_password_change_rejects_missing_special(client, regular_user, user_token):
    """Test password change rejects password without special character."""
    response = client.post(
        "/auth/password",
        json={
            "current_password": "testpass123",
            "new_password": "NoSpecial123"
        },
        cookies={"access_token": user_token}
    )
    assert response.status_code == 400
    assert "special" in response.json()["detail"].lower()


def test_update_me_with_empty_values(client, regular_user, user_token):
    """Test updating user profile with empty string values."""
    response = client.put(
        "/auth/me",
        json={"full_name": "", "department": ""},
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == ""
    assert data["department"] == ""


def test_update_me_response_includes_all_fields(client, regular_user, user_token):
    """Test that profile response includes all expected fields."""
    response = client.put(
        "/auth/me",
        json={"full_name": "Test User", "department": "Engineering"},
        cookies={"access_token": user_token}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify all expected fields are present
    assert "id" in data
    assert "username" in data
    assert "email" in data
    assert "full_name" in data
    assert "department" in data
    assert "role" in data
    assert "is_active" in data
    assert "created_at" in data
    assert "last_login" in data


def test_password_change_same_as_current_fails(client, regular_user, user_token):
    """Test that password change fails if new password is same as current."""
    response = client.post(
        "/auth/password",
        json={
            "current_password": "testpass123",
            "new_password": "testpass123"
        },
        cookies={"access_token": user_token}
    )
    assert response.status_code == 400
