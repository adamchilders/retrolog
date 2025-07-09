import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestAIServices:
    """Test AI-powered features and services."""

    @patch('app.services.genai.GenerativeModel')
    def test_get_journal_entry_insights_success(self, mock_model, client, authenticated_user, test_journal_entry_data, mock_gemini_response):
        """Test successful AI insights generation."""
        # Mock Gemini response
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = mock_gemini_response
        mock_model.return_value = mock_instance
        
        # Create journal entry
        create_response = client.post(
            "/journal-entries/",
            json=test_journal_entry_data,
            headers=authenticated_user["headers"]
        )
        entry_id = create_response.json()["id"]
        
        # Get insights
        response = client.get(
            f"/journal-entries/{entry_id}/insights",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
        assert data["insights"] == mock_gemini_response

    def test_get_insights_entry_not_found(self, client, authenticated_user):
        """Test getting insights for non-existent entry."""
        response = client.get(
            "/journal-entries/999/insights",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404

    def test_get_insights_unauthorized(self, client):
        """Test getting insights without authentication."""
        response = client.get("/journal-entries/1/insights")
        assert response.status_code == 401

    @patch('app.services.genai.GenerativeModel')
    def test_get_insights_ai_error_handling(self, mock_model, client, authenticated_user, test_journal_entry_data):
        """Test AI service error handling."""
        # Mock Gemini to raise an exception
        mock_instance = MagicMock()
        mock_instance.generate_content.side_effect = Exception("API Error")
        mock_model.return_value = mock_instance
        
        # Create journal entry
        create_response = client.post(
            "/journal-entries/",
            json=test_journal_entry_data,
            headers=authenticated_user["headers"]
        )
        entry_id = create_response.json()["id"]
        
        # Get insights - should handle error gracefully
        response = client.get(
            f"/journal-entries/{entry_id}/insights",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
        assert "Could not generate insights" in data["insights"]

    @patch('app.services.genai.GenerativeModel')
    def test_generate_questions_success(self, mock_model, client, authenticated_user, mock_gemini_response):
        """Test successful adaptive question generation."""
        # Mock Gemini response with questions
        questions_response = "What specific steps will you take today?\nHow will you measure success?\nWhat obstacles might you face?"
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = questions_response
        mock_model.return_value = mock_instance
        
        # Generate questions
        request_data = {
            "past_entries": [],
            "time_block": "Morning"
        }
        
        response = client.post(
            "/generate-questions/",
            json=request_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) == 3

    @patch('app.services.genai.GenerativeModel')
    def test_generate_questions_ai_error_fallback(self, mock_model, client, authenticated_user):
        """Test question generation fallback when AI fails."""
        # Mock Gemini to raise an exception
        mock_instance = MagicMock()
        mock_instance.generate_content.side_effect = Exception("API Error")
        mock_model.return_value = mock_instance
        
        request_data = {
            "past_entries": [],
            "time_block": "Morning"
        }
        
        response = client.post(
            "/generate-questions/",
            json=request_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) > 0  # Should have fallback questions

    def test_generate_questions_unauthorized(self, client):
        """Test question generation without authentication."""
        request_data = {
            "past_entries": [],
            "time_block": "Morning"
        }
        
        response = client.post("/generate-questions/", json=request_data)
        assert response.status_code == 401

    @patch('app.services.genai.GenerativeModel')
    def test_get_summary_insights_success(self, mock_model, client, authenticated_user, test_journal_entry_data, mock_gemini_response):
        """Test successful summary insights generation."""
        # Mock Gemini response
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = mock_gemini_response
        mock_model.return_value = mock_instance
        
        # Create some journal entries first
        client.post(
            "/journal-entries/",
            json=test_journal_entry_data,
            headers=authenticated_user["headers"]
        )
        
        # Get summary insights
        response = client.get(
            "/journal-entries/insights/summary?time_range=weekly",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary_insights" in data
        assert data["summary_insights"] == mock_gemini_response

    def test_get_summary_insights_invalid_time_range(self, client, authenticated_user):
        """Test summary insights with invalid time range."""
        response = client.get(
            "/journal-entries/insights/summary?time_range=invalid",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 400

    def test_get_summary_insights_unauthorized(self, client):
        """Test summary insights without authentication."""
        response = client.get("/journal-entries/insights/summary")
        assert response.status_code == 401

    @patch('app.services.genai.GenerativeModel')
    def test_get_summary_insights_no_entries(self, mock_model, client, authenticated_user):
        """Test summary insights when no entries exist."""
        response = client.get(
            "/journal-entries/insights/summary?time_range=weekly",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary_insights" in data
        assert "No journal entries found" in data["summary_insights"]
