import pytest
from fastapi.testclient import TestClient


class TestJournalEntries:
    """Test journal entry CRUD operations."""

    def test_create_journal_entry_success(self, client, authenticated_user, test_journal_entry_data):
        """Test successful journal entry creation."""
        response = client.post(
            "/journal-entries/",
            json=test_journal_entry_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["time_block"] == test_journal_entry_data["time_block"]
        assert "id" in data
        assert "timestamp" in data
        assert data["owner_id"] == authenticated_user["user_id"]
        assert len(data["answers"]) == len(test_journal_entry_data["answers"])
        
        # Check answers
        for i, answer in enumerate(data["answers"]):
            assert answer["question"] == test_journal_entry_data["answers"][i]["question"]
            assert answer["content"] == test_journal_entry_data["answers"][i]["content"]

    def test_create_journal_entry_unauthorized(self, client, test_journal_entry_data):
        """Test journal entry creation without authentication fails."""
        response = client.post("/journal-entries/", json=test_journal_entry_data)
        assert response.status_code == 401

    def test_get_journal_entries_success(self, client, authenticated_user, test_journal_entry_data):
        """Test getting user's journal entries."""
        # Create a journal entry first
        client.post(
            "/journal-entries/",
            json=test_journal_entry_data,
            headers=authenticated_user["headers"]
        )
        
        # Get entries
        response = client.get("/journal-entries/", headers=authenticated_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["time_block"] == test_journal_entry_data["time_block"]

    def test_get_journal_entries_unauthorized(self, client):
        """Test getting journal entries without authentication fails."""
        response = client.get("/journal-entries/")
        assert response.status_code == 401

    def test_get_journal_entries_empty(self, client, authenticated_user):
        """Test getting journal entries when none exist."""
        response = client.get("/journal-entries/", headers=authenticated_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_specific_journal_entry_success(self, client, authenticated_user, test_journal_entry_data):
        """Test getting a specific journal entry."""
        # Create entry
        create_response = client.post(
            "/journal-entries/",
            json=test_journal_entry_data,
            headers=authenticated_user["headers"]
        )
        entry_id = create_response.json()["id"]
        
        # Get specific entry
        response = client.get(
            f"/journal-entries/{entry_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry_id
        assert data["time_block"] == test_journal_entry_data["time_block"]

    def test_get_specific_journal_entry_not_found(self, client, authenticated_user):
        """Test getting non-existent journal entry."""
        response = client.get(
            "/journal-entries/999",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404

    def test_get_specific_journal_entry_unauthorized(self, client):
        """Test getting specific journal entry without authentication."""
        response = client.get("/journal-entries/1")
        assert response.status_code == 401

    def test_update_journal_entry_success(self, client, authenticated_user, test_journal_entry_data):
        """Test successful journal entry update."""
        # Create entry
        create_response = client.post(
            "/journal-entries/",
            json=test_journal_entry_data,
            headers=authenticated_user["headers"]
        )
        entry_id = create_response.json()["id"]
        
        # Update entry
        updated_data = {
            "time_block": "Evening",
            "answers": [
                {
                    "question": "How was your day?",
                    "content": "It was productive and fulfilling"
                }
            ]
        }
        
        response = client.put(
            f"/journal-entries/{entry_id}",
            json=updated_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["time_block"] == updated_data["time_block"]
        assert len(data["answers"]) == len(updated_data["answers"])
        assert data["answers"][0]["content"] == updated_data["answers"][0]["content"]

    def test_update_journal_entry_not_found(self, client, authenticated_user, test_journal_entry_data):
        """Test updating non-existent journal entry."""
        response = client.put(
            "/journal-entries/999",
            json=test_journal_entry_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404

    def test_update_journal_entry_unauthorized(self, client, test_journal_entry_data):
        """Test updating journal entry without authentication."""
        response = client.put("/journal-entries/1", json=test_journal_entry_data)
        assert response.status_code == 401

    def test_journal_entry_isolation_between_users(self, client, test_user_data, test_journal_entry_data):
        """Test that users can only see their own journal entries."""
        # Create first user and entry
        user1_data = test_user_data.copy()
        client.post("/users/", json=user1_data)
        
        login_response = client.post("/token", data=user1_data)
        user1_token = login_response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        
        client.post("/journal-entries/", json=test_journal_entry_data, headers=user1_headers)
        
        # Create second user
        user2_data = {"username": "testuser2", "password": "testpassword456"}
        client.post("/users/", json=user2_data)
        
        login_response = client.post("/token", data=user2_data)
        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User 2 should not see user 1's entries
        response = client.get("/journal-entries/", headers=user2_headers)
        assert response.status_code == 200
        assert len(response.json()) == 0
