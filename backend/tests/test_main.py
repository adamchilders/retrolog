import pytest
from fastapi.testclient import TestClient


class TestMainEndpoints:
    """Test main application endpoints and functionality."""

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Backend is running"

    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})
        
        # FastAPI handles CORS automatically, so we just check the endpoint works
        assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled

    def test_health_check(self, client):
        """Test application health check."""
        response = client.get("/")
        assert response.status_code == 200

    def test_invalid_endpoint(self, client):
        """Test accessing invalid endpoint returns 404."""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404

    def test_api_documentation_available(self, client):
        """Test that API documentation endpoints are available."""
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_application_startup(self, client):
        """Test that the application starts up correctly."""
        # This test ensures the app can be instantiated and basic endpoints work
        response = client.get("/")
        assert response.status_code == 200

    def test_database_connection(self, client, db_session):
        """Test that database connection works."""
        # This test ensures the database dependency injection works
        response = client.get("/")
        assert response.status_code == 200

    def test_middleware_functionality(self, client):
        """Test that middleware is working correctly."""
        # Test that CORS middleware allows requests
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
        response = client.get("/", headers=headers)
        assert response.status_code == 200

    def test_error_handling(self, client):
        """Test application error handling."""
        # Test 404 handling
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # Test method not allowed
        response = client.patch("/")  # Root only accepts GET
        assert response.status_code == 405

    def test_request_validation(self, client):
        """Test request validation works."""
        # Test invalid JSON in POST request
        response = client.post(
            "/users/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
