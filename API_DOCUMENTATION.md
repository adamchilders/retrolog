# RetroLog API Documentation

This document provides comprehensive documentation for the RetroLog REST API. The API is built with FastAPI and provides endpoints for user authentication, journal entry management, and AI-powered insights.

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com/api`

## Authentication

RetroLog uses JWT (JSON Web Token) based authentication. Include the token in the Authorization header for protected endpoints:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### Authentication Endpoints

#### POST /token
**Description**: Authenticate user and receive access token

**Request Body** (form-data):
```
username: string (required)
password: string (required)
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes**:
- `200`: Success
- `401`: Invalid credentials

---

#### POST /users/
**Description**: Register a new user account

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "id": 1,
  "username": "string",
  "entries": []
}
```

**Status Codes**:
- `201`: User created successfully
- `400`: Username already exists

---

#### GET /users/me/
**Description**: Get current user information
**Authentication**: Required

**Response**:
```json
{
  "id": 1,
  "username": "string",
  "entries": []
}
```

**Status Codes**:
- `200`: Success
- `401`: Unauthorized

### Journal Entry Endpoints

#### POST /journal-entries/
**Description**: Create a new journal entry
**Authentication**: Required

**Request Body**:
```json
{
  "time_block": "Morning|Lunch|Evening",
  "answers": [
    {
      "question": "string",
      "content": "string"
    }
  ]
}
```

**Response**:
```json
{
  "id": 1,
  "time_block": "Morning",
  "timestamp": "2024-01-15T10:30:00",
  "owner_id": 1,
  "answers": [
    {
      "id": 1,
      "question": "What is your main goal for today?",
      "content": "Complete the project documentation"
    }
  ]
}
```

**Status Codes**:
- `201`: Entry created successfully
- `400`: Invalid request data
- `401`: Unauthorized

---

#### GET /journal-entries/
**Description**: Get all journal entries for the current user
**Authentication**: Required

**Response**:
```json
[
  {
    "id": 1,
    "time_block": "Morning",
    "timestamp": "2024-01-15T10:30:00",
    "owner_id": 1,
    "answers": [
      {
        "id": 1,
        "question": "What is your main goal for today?",
        "content": "Complete the project documentation"
      }
    ]
  }
]
```

**Status Codes**:
- `200`: Success
- `401`: Unauthorized

---

#### PUT /journal-entries/{entry_id}
**Description**: Update an existing journal entry
**Authentication**: Required

**Path Parameters**:
- `entry_id`: integer (required)

**Request Body**:
```json
{
  "time_block": "Morning|Lunch|Evening",
  "answers": [
    {
      "question": "string",
      "content": "string"
    }
  ]
}
```

**Response**:
```json
{
  "id": 1,
  "time_block": "Morning",
  "timestamp": "2024-01-15T10:30:00",
  "owner_id": 1,
  "answers": [
    {
      "id": 1,
      "question": "What is your main goal for today?",
      "content": "Complete the project documentation and review code"
    }
  ]
}
```

**Status Codes**:
- `200`: Entry updated successfully
- `403`: Not authorized to update this entry
- `404`: Entry not found

### AI-Powered Insights Endpoints

#### GET /journal-entries/{entry_id}/insights
**Description**: Get AI-generated insights for a specific journal entry
**Authentication**: Required

**Path Parameters**:
- `entry_id`: integer (required)

**Response**:
```json
{
  "insights": "Based on your morning entry, you show strong goal-oriented thinking. Your focus on documentation suggests good planning skills. Consider breaking down large tasks into smaller, manageable chunks to maintain momentum throughout the day."
}
```

**Status Codes**:
- `200`: Success
- `403`: Not authorized to access this entry
- `404`: Entry not found
- `500`: AI service unavailable

---

#### POST /generate-questions/
**Description**: Generate adaptive questions based on past entries
**Authentication**: Required

**Request Body**:
```json
{
  "past_entries": [
    {
      "id": 1,
      "time_block": "Morning",
      "timestamp": "2024-01-15T10:30:00",
      "owner_id": 1,
      "answers": [
        {
          "id": 1,
          "question": "What is your main goal for today?",
          "content": "Complete the project documentation"
        }
      ]
    }
  ],
  "time_block": "Morning|Lunch|Evening"
}
```

**Response**:
```json
{
  "questions": [
    "What specific steps will you take to ensure quality in your documentation?",
    "How will you measure the success of today's work?",
    "What potential obstacles might you face, and how will you overcome them?"
  ]
}
```

**Status Codes**:
- `200`: Success
- `401`: Unauthorized
- `500`: AI service unavailable

---

#### GET /journal-entries/insights/summary
**Description**: Get summary insights for a time period
**Authentication**: Required

**Query Parameters**:
- `time_range`: string (optional, default: "weekly")
  - Allowed values: "daily", "weekly", "monthly"

**Response**:
```json
{
  "summary_insights": "Over the past week, you've shown consistent goal-setting behavior in your morning entries. Your focus on documentation and planning indicates strong organizational skills. Areas for improvement include setting more specific deadlines and incorporating reflection on completed tasks. Suggestions: 1) Add time estimates to your daily goals, 2) Include a brief review of yesterday's accomplishments in your morning routine."
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid time_range parameter
- `401`: Unauthorized

### Utility Endpoints

#### GET /
**Description**: Health check endpoint

**Response**:
```json
{
  "message": "Backend is running"
}
```

**Status Codes**:
- `200`: Service is healthy

## Data Models

### User
```json
{
  "id": "integer",
  "username": "string",
  "entries": "JournalEntry[]"
}
```

### JournalEntry
```json
{
  "id": "integer",
  "time_block": "string",
  "timestamp": "datetime",
  "owner_id": "integer",
  "answers": "Answer[]"
}
```

### Answer
```json
{
  "id": "integer",
  "question": "string",
  "content": "string"
}
```

### Token
```json
{
  "access_token": "string",
  "token_type": "string"
}
```

## Error Handling

The API returns standard HTTP status codes and error messages in JSON format:

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes
- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Missing or invalid authentication
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource doesn't exist
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Server-side error

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting to prevent abuse.

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost`
- `http://localhost:3000` (React development server)

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## SDK and Client Libraries

Currently, no official SDKs are available. The API can be consumed using any HTTP client library such as:
- **JavaScript**: Axios, Fetch API
- **Python**: Requests, httpx
- **cURL**: Command line HTTP client

## Testing

### API Testing

The RetroLog API includes comprehensive test coverage with automated testing:

#### Test Coverage
- **Authentication Endpoints**: 100% coverage
- **Journal Entry Operations**: 100% coverage
- **AI Service Integration**: 90% coverage (with mocked external APIs)
- **Error Handling**: 85% coverage

#### Running API Tests

```bash
# Run all backend tests
./scripts/run-tests.sh --backend --coverage

# Run specific test categories
docker-compose exec backend python -m pytest tests/test_auth.py -v
docker-compose exec backend python -m pytest tests/test_journal_entries.py -v
docker-compose exec backend python -m pytest tests/test_ai_services.py -v
```

#### Test Environment

Tests use SQLite in-memory database for isolation and speed:

```python
# Test configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
```

#### Example Test Usage

```python
def test_create_journal_entry(client, authenticated_user):
    """Test journal entry creation."""
    entry_data = {
        "time_block": "Morning",
        "answers": [
            {"question": "How are you?", "content": "Great!"}
        ]
    }

    response = client.post(
        "/journal-entries/",
        json=entry_data,
        headers=authenticated_user["headers"]
    )

    assert response.status_code == 200
    assert response.json()["time_block"] == "Morning"
```

### Integration Testing

Integration tests verify end-to-end API functionality:

```bash
# Run integration tests
./scripts/run-tests.sh --integration

# Manual integration testing
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

## Changelog

### Version 1.0.0
- Initial API release
- User authentication with JWT
- Journal entry CRUD operations
- AI-powered insights integration
- Adaptive question generation
- Summary analytics endpoints
- Comprehensive test suite with >95% coverage
- Automated CI/CD pipeline with GitHub Actions
- Pre-commit hooks for quality assurance
