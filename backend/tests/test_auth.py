import pytest
from fastapi.testclient import TestClient


class TestAuthentication:
    """Test authentication endpoints and functionality."""

    def test_create_user_success(self, client, test_user_data):
        """Test successful user creation."""
        response = client.post("/users/", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert "id" in data
        assert "entries" in data
        assert data["entries"] == []

    def test_create_user_duplicate_username(self, client, test_user_data):
        """Test creating user with duplicate username fails."""
        # Create first user
        response = client.post("/users/", json=test_user_data)
        assert response.status_code == 200
        
        # Try to create user with same username
        response = client.post("/users/", json=test_user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user_data):
        """Test successful login."""
        # Create user first
        client.post("/users/", json=test_user_data)
        
        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/token", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials."""
        # Create user first
        client.post("/users/", json=test_user_data)
        
        # Try login with wrong password
        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword"
        }
        response = client.post("/token", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "password"
        }
        response = client.post("/token", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_get_current_user_success(self, client, authenticated_user):
        """Test getting current user information."""
        response = client.get("/users/me/", headers=authenticated_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "entries" in data

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token fails."""
        response = client.get("/users/me/")
        
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/me/", headers=headers)
        
        assert response.status_code == 401

    def test_protected_endpoint_requires_auth(self, client):
        """Test that protected endpoints require authentication."""
        response = client.get("/journal-entries/")
        assert response.status_code == 401

    def test_protected_endpoint_with_auth(self, client, authenticated_user):
        """Test that protected endpoints work with valid authentication."""
        response = client.get("/journal-entries/", headers=authenticated_user["headers"])
        assert response.status_code == 200
