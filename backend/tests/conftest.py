import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, get_db
from app.database import Base
from app import models

# Test database URL - using SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


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
    """Create a test client with database dependency override."""
    def override_get_db_for_test():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db_for_test
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "password": "testpassword123"
    }


@pytest.fixture
def test_journal_entry_data():
    """Sample journal entry data for testing."""
    return {
        "time_block": "Morning",
        "answers": [
            {
                "question": "What is your main goal for today?",
                "content": "Complete the project documentation"
            },
            {
                "question": "How are you feeling this morning?",
                "content": "Energetic and focused"
            }
        ]
    }


@pytest.fixture
def authenticated_user(client, test_user_data, db_session):
    """Create a user and return authentication token."""
    # Create user
    response = client.post("/users/", json=test_user_data)
    assert response.status_code == 200
    
    # Login and get token
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    user_id = client.get("/users/me/", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    
    return {
        "token": token,
        "user_id": user_id,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def mock_gemini_response():
    """Mock response for Gemini AI."""
    return "This is a mock AI insight response with actionable suggestions."


# Set environment variables for testing
os.environ["GOOGLE_API_KEY"] = "test_api_key"
os.environ["SECRET_KEY"] = "test_secret_key"
