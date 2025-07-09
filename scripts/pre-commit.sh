#!/bin/bash

# RetroLog Pre-commit Hook
# This script runs tests before allowing commits

set -e  # Exit on any error

echo "🔍 Running pre-commit checks..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_status "Docker is running"
}

# Function to run backend tests
run_backend_tests() {
    print_info "Running backend tests..."
    
    # Check if backend container is running
    if ! docker-compose ps backend | grep -q "Up"; then
        print_warning "Backend container not running. Starting services..."
        docker-compose up -d backend db
        sleep 10  # Wait for services to be ready
    fi
    
    # Install test dependencies if needed
    docker-compose exec -T backend pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
    
    # Run tests
    if docker-compose exec -T backend python -m pytest --tb=short -v; then
        print_status "Backend tests passed"
        return 0
    else
        print_error "Backend tests failed"
        return 1
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    print_info "Running frontend tests..."
    
    # Check if frontend dependencies are installed
    if [ ! -d "frontend/node_modules" ]; then
        print_warning "Frontend dependencies not installed. Installing..."
        cd frontend && npm install && cd ..
    fi
    
    # Run tests
    cd frontend
    if npm run test:ci; then
        print_status "Frontend tests passed"
        cd ..
        return 0
    else
        print_error "Frontend tests failed"
        cd ..
        return 1
    fi
}

# Function to run linting (if available)
run_linting() {
    print_info "Running code quality checks..."
    
    # Backend linting (basic Python syntax check)
    if command -v python3 > /dev/null; then
        if python3 -m py_compile backend/app/*.py; then
            print_status "Backend syntax check passed"
        else
            print_error "Backend syntax check failed"
            return 1
        fi
    fi
    
    # Frontend TypeScript compilation check
    cd frontend
    if npx tsc --noEmit; then
        print_status "Frontend TypeScript check passed"
        cd ..
    else
        print_error "Frontend TypeScript check failed"
        cd ..
        return 1
    fi
}

# Function to check for sensitive data
check_sensitive_data() {
    print_info "Checking for sensitive data..."

    # Check for API keys in staged files, excluding test files and documentation
    if git diff --cached --name-only | grep -v -E "(test|spec|\.md$|\.yml$|conftest\.py)" | xargs grep -l "GOOGLE_API_KEY.*[^=]test\|SECRET_KEY.*[^=]test\|password.*[^=]test" 2>/dev/null; then
        print_error "Potential sensitive data found in staged files!"
        print_error "Please remove API keys, passwords, or other sensitive data before committing."
        print_error "Test values and documentation are allowed."
        return 1
    fi

    print_status "No sensitive data detected"
}

# Main execution
main() {
    echo "🚀 RetroLog Pre-commit Checks"
    echo "============================="
    
    # Check for sensitive data first
    if ! check_sensitive_data; then
        exit 1
    fi
    
    # Check Docker
    check_docker
    
    # Run linting
    if ! run_linting; then
        print_error "Code quality checks failed. Please fix the issues and try again."
        exit 1
    fi
    
    # Run backend tests
    if ! run_backend_tests; then
        print_error "Backend tests failed. Please fix the failing tests and try again."
        exit 1
    fi
    
    # Run frontend tests
    if ! run_frontend_tests; then
        print_error "Frontend tests failed. Please fix the failing tests and try again."
        exit 1
    fi
    
    echo ""
    print_status "All pre-commit checks passed! 🎉"
    print_info "Your commit is ready to proceed."
    echo ""
}

# Run main function
main "$@"
