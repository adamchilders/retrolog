# Contributing to RetroLog

Thank you for your interest in contributing to RetroLog! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git
- Google Gemini API key (for AI features)

### Setup Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd retrolog
   ```

2. **Run the setup script**
   ```bash
   ./setup.sh
   ```

3. **Set up pre-commit hooks**
   ```bash
   ./scripts/setup-hooks.sh
   ```

4. **Or manual setup**
   ```bash
   # Copy environment file
   cp backend/.env.example backend/.env

   # Add your Google Gemini API key to backend/.env
   # Build and start the application
   docker-compose up --build
   ```

## Development Workflow

### Making Changes

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style and conventions
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   ./scripts/run-tests.sh --all

   # Run specific test suites
   ./scripts/run-tests.sh --backend --coverage
   ./scripts/run-tests.sh --frontend --coverage
   ./scripts/run-tests.sh --integration

   # Run tests in watch mode (frontend)
   ./scripts/run-tests.sh --frontend --watch
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### Pull Request Process

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Include screenshots for UI changes
   - Ensure all tests pass

3. **Code Review**
   - Address any feedback from reviewers
   - Make necessary changes and push updates

## Code Style Guidelines

### Backend (Python)
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small

### Frontend (TypeScript/React)
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Keep components small and focused

### Database
- Use descriptive table and column names
- Include proper foreign key relationships
- Add appropriate indexes for performance

## Testing

RetroLog has comprehensive test coverage with automated testing at multiple levels:

### Test Types

1. **Unit Tests**: Test individual functions and components
2. **Integration Tests**: Test API endpoints and component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Security Tests**: Automated vulnerability scanning

### Running Tests

**All Tests:**
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

### Test Coverage Requirements

- **Minimum Coverage**: 80% for both backend and frontend
- **Critical Paths**: 95% coverage for authentication and data handling
- **New Features**: Must include comprehensive tests
- **Bug Fixes**: Must include regression tests

### Pre-commit Testing

Tests run automatically before commits:

```bash
# Set up once
./scripts/setup-hooks.sh

# Tests run automatically on commit
git commit -m "your changes"

# Bypass in emergencies (not recommended)
git commit --no-verify -m "emergency fix"
```

### Continuous Integration

Our CI/CD pipeline ensures code quality through automated testing:

#### GitHub Actions Pipeline
- **Multi-Stage Testing**: Backend, frontend, integration, and security tests
- **Multiple Environments**: Python 3.9+ and Node.js 18+ compatibility
- **Parallel Execution**: Tests run concurrently for faster feedback
- **Artifact Management**: Build artifacts stored for deployment

#### Pipeline Stages
1. **Backend Tests**: Unit tests with MySQL database integration
2. **Frontend Tests**: React component and integration tests
3. **Integration Tests**: End-to-end service communication
4. **Security Scanning**: Trivy vulnerability detection
5. **Code Quality**: Automated linting and formatting validation

#### Quality Gates
- **Test Coverage**: Minimum 80% coverage required
- **Security Scan**: No high/critical vulnerabilities allowed
- **Code Quality**: All linting checks must pass
- **Build Success**: All environments must build successfully

#### Viewing Results
- **GitHub Actions**: Check the Actions tab for detailed results
- **Coverage Reports**: Codecov integration provides coverage metrics
- **Security Reports**: GitHub Security tab shows vulnerability findings
- **Quality Metrics**: PR checks show code quality status

## Documentation

- Update README.md for user-facing changes
- Update API_DOCUMENTATION.md for API changes
- Add inline code comments for complex logic
- Include examples in documentation

## Reporting Issues

When reporting issues, please include:

1. **Environment Information**
   - Operating system
   - Docker version
   - Browser (for frontend issues)

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Screenshots if applicable

3. **Error Messages**
   - Full error messages
   - Relevant log output

## Feature Requests

For feature requests, please:

1. Check existing issues to avoid duplicates
2. Provide a clear use case
3. Explain the expected behavior
4. Consider the impact on existing functionality

## Security

If you discover a security vulnerability, please:

1. **Do not** create a public issue
2. Email the maintainers directly
3. Provide detailed information about the vulnerability
4. Allow time for the issue to be addressed before disclosure

## Questions and Support

- Check the documentation first
- Search existing issues
- Create a new issue with the "question" label
- Join our community discussions (if available)

## License

By contributing to RetroLog, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in the project's README.md file and release notes.

Thank you for contributing to RetroLog! 🚀
