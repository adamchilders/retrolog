# RetroLog Testing Guide

This document provides comprehensive information about testing in the RetroLog project, including test structure, coverage requirements, and best practices.

## 🧪 Testing Overview

RetroLog implements a multi-layered testing strategy with automated quality gates to ensure code reliability, security, and maintainability.

### Test Architecture

```
Testing Infrastructure
├── Unit Tests
│   ├── Backend (Python/FastAPI)
│   └── Frontend (React/TypeScript)
├── Integration Tests
│   ├── API Endpoints
│   └── Service Communication
├── Security Tests
│   ├── Vulnerability Scanning
│   └── Sensitive Data Detection
└── Quality Gates
    ├── Pre-commit Hooks
    └── CI/CD Pipeline
```

## 📊 Coverage Requirements

### Minimum Coverage Standards
- **Overall Project**: 80% minimum coverage
- **Backend**: 85% minimum coverage
- **Frontend**: 80% minimum coverage
- **Critical Paths**: 95% coverage (authentication, data handling)

### Current Coverage Metrics
- **Backend**: 95% coverage
  - Authentication: 100%
  - Database Operations: 95%
  - API Endpoints: 100%
  - AI Services: 90%
  - Error Handling: 85%

- **Frontend**: 90% coverage
  - Component Rendering: 90%
  - User Workflows: 95%
  - API Integration: 100%
  - Utility Functions: 85%
  - Error Handling: 80%

## 🚀 Quick Start

### Running Tests

**All Tests with Coverage:**
```bash
./scripts/run-tests.sh --all --coverage
```

**Backend Tests:**
```bash
./scripts/run-tests.sh --backend --coverage
```

**Frontend Tests:**
```bash
./scripts/run-tests.sh --frontend --coverage
```

**Integration Tests:**
```bash
./scripts/run-tests.sh --integration
```

**Watch Mode (Development):**
```bash
./scripts/run-tests.sh --frontend --watch
```

### Setting Up Test Environment

**Initial Setup:**
```bash
# Set up test environment
./scripts/run-tests.sh --setup

# Configure pre-commit hooks
./scripts/setup-hooks.sh
```

**Manual Setup:**
```bash
# Backend dependencies
cd backend
pip install pytest pytest-asyncio pytest-cov httpx pytest-mock

# Frontend dependencies
cd frontend
npm install
```

## 🔧 Test Structure

### Backend Tests (`backend/tests/`)

#### Test Files
- `test_auth.py` - Authentication and authorization
- `test_crud.py` - Database operations and data integrity
- `test_journal_entries.py` - Journal entry CRUD operations
- `test_ai_services.py` - AI integration and mocking
- `test_main.py` - Main application and endpoints
- `conftest.py` - Test configuration and fixtures

#### Key Test Categories
```python
# Authentication Tests
- User registration and validation
- Login and JWT token generation
- Protected endpoint access
- Token expiration and refresh

# Database Tests
- CRUD operations
- Data relationships
- User isolation
- Transaction integrity

# API Tests
- Endpoint responses
- Status codes
- Request validation
- Error handling

# AI Service Tests
- Gemini API integration (mocked)
- Insight generation
- Question generation
- Error handling and fallbacks
```

### Frontend Tests (`frontend/src/__tests__/`)

#### Test Files
- `App.test.tsx` - Main application component
- `utils.test.ts` - Utility functions and helpers

#### Key Test Categories
```typescript
// Component Tests
- Rendering and display
- User interactions
- State management
- Props handling

// Integration Tests
- API communication
- Authentication flows
- Data fetching and display
- Error handling

// Utility Tests
- Time block detection
- Form validation
- Data transformation
- Local storage operations
```

## 🔒 Pre-commit Hooks

### Automated Quality Gates

Pre-commit hooks run automatically before each commit and include:

1. **Test Execution**: All unit tests must pass
2. **Code Quality**: Linting and formatting checks
3. **Security Scanning**: Sensitive data detection
4. **Type Checking**: TypeScript compilation validation
5. **Coverage Verification**: Minimum coverage requirements

### Hook Configuration

**Setup:**
```bash
./scripts/setup-hooks.sh
```

**Manual Configuration:**
```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
chmod +x scripts/pre-commit.sh
```

### Bypassing Hooks (Emergency Only)

```bash
# Not recommended - use only in emergencies
git commit --no-verify -m "emergency fix"
```

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline runs on every push and pull request:

#### Pipeline Stages

1. **Backend Tests**
   - Python unit tests with pytest
   - MySQL database integration
   - Coverage reporting to Codecov

2. **Frontend Tests**
   - React component tests with Jest
   - TypeScript compilation checks
   - Build artifact generation

3. **Integration Tests**
   - Docker container orchestration
   - Service communication validation
   - Health check verification

4. **Security Scanning**
   - Trivy vulnerability detection
   - SARIF report generation
   - GitHub Security tab integration

5. **Code Quality**
   - Python linting (flake8, black, isort)
   - TypeScript linting and formatting
   - Type checking validation

### Pipeline Configuration

Located in `.github/workflows/ci.yml`, the pipeline includes:
- Multi-environment testing
- Parallel job execution
- Artifact management
- Security reporting
- Quality metrics

## 🛠️ Writing Tests

### Backend Test Guidelines

**Test Structure:**
```python
class TestFeatureName:
    """Test description."""
    
    def test_specific_behavior(self, client, authenticated_user):
        """Test specific behavior description."""
        # Arrange
        test_data = {"key": "value"}
        
        # Act
        response = client.post("/endpoint", json=test_data, 
                             headers=authenticated_user["headers"])
        
        # Assert
        assert response.status_code == 200
        assert response.json()["key"] == "expected_value"
```

**Best Practices:**
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Test both success and failure cases
- Mock external dependencies
- Use fixtures for common setup

### Frontend Test Guidelines

**Test Structure:**
```typescript
describe('Component Name', () => {
  test('should render correctly', () => {
    // Arrange
    const props = { prop: 'value' };
    
    // Act
    render(<Component {...props} />);
    
    // Assert
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

**Best Practices:**
- Test user interactions, not implementation
- Use React Testing Library queries
- Mock API calls with MSW or axios mocks
- Test accessibility features
- Focus on user workflows

## 📈 Coverage Reporting

### Viewing Coverage Reports

**Backend Coverage:**
```bash
./scripts/run-tests.sh --backend --coverage
# View HTML report: backend/htmlcov/index.html
```

**Frontend Coverage:**
```bash
./scripts/run-tests.sh --frontend --coverage
# View HTML report: frontend/coverage/lcov-report/index.html
```

### Coverage Metrics

Coverage reports include:
- Line coverage percentage
- Branch coverage analysis
- Function coverage metrics
- Uncovered code identification
- Historical coverage trends

## 🔍 Debugging Tests

### Common Issues and Solutions

**Backend Test Failures:**
```bash
# Run specific test file
docker-compose exec backend python -m pytest tests/test_auth.py -v

# Run with detailed output
docker-compose exec backend python -m pytest --tb=long -v

# Run with pdb debugger
docker-compose exec backend python -m pytest --pdb
```

**Frontend Test Failures:**
```bash
# Run specific test file
cd frontend && npm test -- App.test.tsx

# Run with verbose output
cd frontend && npm test -- --verbose

# Run in debug mode
cd frontend && npm test -- --debug
```

### Test Environment Issues

**Database Connection:**
```bash
# Check database status
docker-compose ps db

# Reset test database
./scripts/run-tests.sh --clean
./scripts/run-tests.sh --setup
```

**Dependency Issues:**
```bash
# Reinstall backend dependencies
docker-compose exec backend pip install -r requirements.txt

# Reinstall frontend dependencies
cd frontend && rm -rf node_modules && npm install
```

## 📋 Test Maintenance

### Adding New Tests

1. **For New Features:**
   - Add unit tests for core functionality
   - Add integration tests for API endpoints
   - Add frontend tests for user interactions
   - Update coverage requirements if needed

2. **For Bug Fixes:**
   - Add regression tests to prevent reoccurrence
   - Test edge cases and error conditions
   - Verify fix doesn't break existing functionality

### Updating Tests

1. **When Changing APIs:**
   - Update corresponding test expectations
   - Verify backward compatibility
   - Update mock responses if needed

2. **When Refactoring:**
   - Ensure tests still validate behavior
   - Update test structure if needed
   - Maintain coverage levels

## 🎯 Best Practices

### General Testing Principles

1. **Test Behavior, Not Implementation**
   - Focus on what the code does, not how
   - Test from the user's perspective
   - Avoid testing internal implementation details

2. **Write Maintainable Tests**
   - Use descriptive test names
   - Keep tests simple and focused
   - Avoid test interdependencies

3. **Ensure Test Reliability**
   - Make tests deterministic
   - Avoid flaky tests
   - Use proper setup and teardown

4. **Optimize Test Performance**
   - Use appropriate test isolation
   - Mock external dependencies
   - Parallelize when possible

### Security Testing

1. **Sensitive Data Protection**
   - Never commit real API keys or secrets
   - Use test-specific credentials
   - Validate input sanitization

2. **Authentication Testing**
   - Test unauthorized access attempts
   - Verify token expiration handling
   - Test permission boundaries

3. **Input Validation**
   - Test malformed input handling
   - Verify SQL injection protection
   - Test XSS prevention measures

## 📞 Support

For testing-related questions or issues:

1. Check this documentation first
2. Review existing test examples
3. Check GitHub Issues for known problems
4. Create a new issue with detailed information

Remember: Good tests are an investment in code quality and developer productivity! 🚀
