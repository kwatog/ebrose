import os
import pytest
from unittest.mock import patch


@pytest.fixture
def rate_limited_client(db_session, admin_user):
    """Client with rate limiting enabled."""
    import app.main
    from app.database import get_db
    from fastapi.testclient import TestClient
    
    import app.rate_limiter
    app.rate_limiter._login_rate_limiter = None
    app.rate_limiter._global_ip_rate_limiter = None
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.main.app.dependency_overrides[get_db] = override_get_db

    with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "true"}):
        from app.config import get_settings
        get_settings.cache_clear()
        
        with TestClient(app.main.app) as test_client:
            yield test_client
        
        get_settings.cache_clear()

    app.main.app.dependency_overrides.clear()
    app.rate_limiter._login_rate_limiter = None
    app.rate_limiter._global_ip_rate_limiter = None


def test_rate_limiting_blocks_after_max_attempts(rate_limited_client, admin_user):
    """Rate limiter blocks after exceeding max attempts."""
    for i in range(5):
        response = rate_limited_client.post(
            "/auth/login",
            data={"username": "testadmin", "password": "wrongpassword"}
        )
        assert response.status_code == 401, f"Attempt {i+1} should return 401"

    response = rate_limited_client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "wrongpassword"}
    )
    assert response.status_code == 429
    assert "Too many attempts" in response.json()["detail"]
    assert "Retry-After" in response.headers


def test_rate_limiting_resets_on_successful_login(rate_limited_client, admin_user):
    """Rate limit resets after successful login."""
    for i in range(4):
        response = rate_limited_client.post(
            "/auth/login",
            data={"username": "testadmin", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    response = rate_limited_client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "testpass123"}
    )
    assert response.status_code == 200

    for i in range(4):
        response = rate_limited_client.post(
            "/auth/login",
            data={"username": "testadmin", "password": "wrongpassword"}
        )
        assert response.status_code == 401, f"Attempt {i+1} after reset should return 401"


def test_rate_limiting_per_user(rate_limited_client, admin_user, db_session):
    """Rate limiting is per IP+username combination."""
    from app.auth import get_password_hash
    from app import models
    
    other_user = models.User(
        username="otheruser",
        hashed_password=get_password_hash("otherpass123"),
        role="User",
        email="other@test.com",
        full_name="Other User"
    )
    db_session.add(other_user)
    db_session.commit()

    for i in range(5):
        rate_limited_client.post(
            "/auth/login",
            data={"username": "testadmin", "password": "wrongpassword"}
        )

    response = rate_limited_client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "wrongpassword"}
    )
    assert response.status_code == 429

    response = rate_limited_client.post(
        "/auth/login",
        data={"username": "otheruser", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_rate_limiter_disabled_in_test_environment(client, admin_user):
    """Rate limiting is disabled when ENVIRONMENT=test."""
    for i in range(10):
        response = client.post(
            "/auth/login",
            data={"username": "testadmin", "password": "wrongpassword"}
        )
        assert response.status_code == 401, f"Attempt {i+1} should return 401 (rate limiting disabled)"
