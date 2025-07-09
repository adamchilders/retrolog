#!/bin/bash

# Test runner script for RetroLog
# This script provides various testing options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}$1${NC}"
    echo "=================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

show_help() {
    echo "RetroLog Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -a, --all               Run all tests (backend + frontend)"
    echo "  -b, --backend           Run backend tests only"
    echo "  -f, --frontend          Run frontend tests only"
    echo "  -c, --coverage          Run tests with coverage report"
    echo "  -w, --watch             Run frontend tests in watch mode"
    echo "  -i, --integration       Run integration tests"
    echo "  --setup                 Set up test environment"
    echo "  --clean                 Clean test artifacts"
    echo ""
    echo "Examples:"
    echo "  $0 --all                # Run all tests"
    echo "  $0 --backend --coverage # Run backend tests with coverage"
    echo "  $0 --frontend --watch   # Run frontend tests in watch mode"
}

setup_test_environment() {
    print_header "Setting up test environment"
    
    # Start Docker services
    print_info "Starting Docker services..."
    docker-compose up -d db
    
    # Install backend dependencies
    print_info "Installing backend test dependencies..."
    docker-compose exec backend pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
    
    # Install frontend dependencies
    if [ ! -d "frontend/node_modules" ]; then
        print_info "Installing frontend dependencies..."
        cd frontend && npm install && cd ..
    fi
    
    print_success "Test environment ready"
}

run_backend_tests() {
    local coverage_flag=""
    if [ "$1" = "coverage" ]; then
        coverage_flag="--cov=app --cov-report=term-missing --cov-report=html:backend/htmlcov"
    fi
    
    print_header "Running Backend Tests"
    
    # Ensure backend is running
    if ! docker-compose ps backend | grep -q "Up"; then
        print_info "Starting backend services..."
        docker-compose up -d backend db
        sleep 5
    fi
    
    # Run tests
    if docker-compose exec -T backend python -m pytest $coverage_flag -v; then
        print_success "Backend tests passed"
        if [ "$1" = "coverage" ]; then
            print_info "Coverage report generated in backend/htmlcov/"
        fi
        return 0
    else
        print_error "Backend tests failed"
        return 1
    fi
}

run_frontend_tests() {
    local mode="$1"
    
    print_header "Running Frontend Tests"
    
    cd frontend
    
    case "$mode" in
        "coverage")
            if npm run test:ci; then
                print_success "Frontend tests passed with coverage"
                cd ..
                return 0
            else
                print_error "Frontend tests failed"
                cd ..
                return 1
            fi
            ;;
        "watch")
            print_info "Starting frontend tests in watch mode (press 'q' to quit)"
            npm test
            cd ..
            return 0
            ;;
        *)
            if npm run test:ci; then
                print_success "Frontend tests passed"
                cd ..
                return 0
            else
                print_error "Frontend tests failed"
                cd ..
                return 1
            fi
            ;;
    esac
}

run_integration_tests() {
    print_header "Running Integration Tests"
    
    # Ensure all services are running
    print_info "Starting all services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_info "Waiting for services to be ready..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/ 2>/dev/null; do sleep 2; done' || {
        print_error "Backend service failed to start"
        return 1
    }
    
    timeout 60 bash -c 'until curl -f http://localhost:3000/ 2>/dev/null; do sleep 2; done' || {
        print_error "Frontend service failed to start"
        return 1
    }
    
    # Run integration tests
    print_info "Testing API endpoints..."
    
    # Test health endpoint
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Test API documentation
    if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
        print_success "API documentation accessible"
    else
        print_error "API documentation not accessible"
        return 1
    fi
    
    # Test frontend
    if curl -f http://localhost:3000/ > /dev/null 2>&1; then
        print_success "Frontend accessible"
    else
        print_error "Frontend not accessible"
        return 1
    fi
    
    print_success "All integration tests passed"
}

clean_test_artifacts() {
    print_header "Cleaning test artifacts"
    
    # Remove coverage reports
    rm -rf backend/htmlcov/
    rm -rf backend/.coverage
    rm -rf frontend/coverage/
    
    # Remove test databases
    rm -f backend/test.db
    
    # Stop and remove test containers
    docker-compose down -v
    
    print_success "Test artifacts cleaned"
}

# Parse command line arguments
BACKEND=false
FRONTEND=false
ALL=false
COVERAGE=false
WATCH=false
INTEGRATION=false
SETUP=false
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -a|--all)
            ALL=true
            shift
            ;;
        -b|--backend)
            BACKEND=true
            shift
            ;;
        -f|--frontend)
            FRONTEND=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -w|--watch)
            WATCH=true
            shift
            ;;
        -i|--integration)
            INTEGRATION=true
            shift
            ;;
        --setup)
            SETUP=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute based on flags
if [ "$CLEAN" = true ]; then
    clean_test_artifacts
    exit 0
fi

if [ "$SETUP" = true ]; then
    setup_test_environment
    exit 0
fi

# Default to all tests if no specific test type is specified
if [ "$BACKEND" = false ] && [ "$FRONTEND" = false ] && [ "$INTEGRATION" = false ] && [ "$ALL" = false ]; then
    ALL=true
fi

# Run tests
exit_code=0

if [ "$ALL" = true ] || [ "$BACKEND" = true ]; then
    if [ "$COVERAGE" = true ]; then
        run_backend_tests "coverage" || exit_code=1
    else
        run_backend_tests || exit_code=1
    fi
fi

if [ "$ALL" = true ] || [ "$FRONTEND" = true ]; then
    if [ "$WATCH" = true ]; then
        run_frontend_tests "watch"
    elif [ "$COVERAGE" = true ]; then
        run_frontend_tests "coverage" || exit_code=1
    else
        run_frontend_tests || exit_code=1
    fi
fi

if [ "$INTEGRATION" = true ]; then
    run_integration_tests || exit_code=1
fi

if [ $exit_code -eq 0 ]; then
    echo ""
    print_success "All requested tests completed successfully! 🎉"
else
    echo ""
    print_error "Some tests failed. Please check the output above."
fi

exit $exit_code
