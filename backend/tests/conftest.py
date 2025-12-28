import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(db_session):
    """Create an admin user for testing."""
    from app.auth import get_password_hash

    user = models.User(
        username="testadmin",
        hashed_password=get_password_hash("testpass123"),
        role="Admin",
        email="admin@test.com"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def manager_user(db_session):
    """Create a manager user for testing."""
    from app.auth import get_password_hash

    user = models.User(
        username="testmanager",
        hashed_password=get_password_hash("testpass123"),
        role="Manager",
        email="manager@test.com"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def regular_user(db_session):
    """Create a regular user for testing."""
    from app.auth import get_password_hash

    user = models.User(
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        role="User",
        email="user@test.com"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_group(db_session, admin_user):
    """Create a test group."""
    group = models.UserGroup(
        name="Test Group",
        description="A test group",
        created_by=admin_user.id
    )
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)
    return group


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """Get JWT token for admin user."""
    response = client.post(
        "/auth/login",
        json={"username": "testadmin", "password": "testpass123"}
    )
    assert response.status_code == 200
    return response.cookies.get("access_token")


@pytest.fixture(scope="function")
def manager_token(client, manager_user):
    """Get JWT token for manager user."""
    response = client.post(
        "/auth/login",
        json={"username": "testmanager", "password": "testpass123"}
    )
    assert response.status_code == 200
    return response.cookies.get("access_token")


@pytest.fixture(scope="function")
def user_token(client, regular_user):
    """Get JWT token for regular user."""
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    return response.cookies.get("access_token")
