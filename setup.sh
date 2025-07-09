#!/bin/bash

# RetroLog Setup Script
# This script helps you set up the RetroLog application quickly

echo "🚀 RetroLog Setup Script"
echo "========================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "📝 Setting up environment configuration..."
    
    # Copy example env file
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from example"
    
    echo ""
    echo "⚠️  IMPORTANT: You need to add your Google Gemini API key!"
    echo "   1. Get your API key from: https://makersuite.google.com/app/apikey"
    echo "   2. Edit backend/.env and replace 'your_gemini_api_key_here' with your actual API key"
    echo ""
    read -p "Press Enter when you've added your API key to backend/.env..."
else
    echo "✅ Environment file already exists"
fi

# Build and start the application
echo ""
echo "🔨 Building and starting RetroLog..."
echo "This may take a few minutes on first run..."

if command -v docker-compose &> /dev/null; then
    docker-compose up --build -d
else
    docker compose up --build -d
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 RetroLog is now running!"
    echo ""
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "🧪 Next Steps - Set up testing:"
    echo "   ./scripts/setup-hooks.sh    # Set up pre-commit hooks"
    echo "   ./scripts/run-tests.sh --all # Run all tests"
    echo ""
    echo "📋 Useful Commands:"
    echo "   ./scripts/run-tests.sh --all --coverage  # Run tests with coverage"
    echo "   ./scripts/run-tests.sh --frontend --watch # Frontend tests in watch mode"
    echo ""
    echo "🛑 To stop the application:"
    if command -v docker-compose &> /dev/null; then
        echo "   docker-compose down"
    else
        echo "   docker compose down"
    fi
    echo ""
    echo "📊 To view logs:"
    if command -v docker-compose &> /dev/null; then
        echo "   docker-compose logs -f"
    else
        echo "   docker compose logs -f"
    fi
else
    echo "❌ Failed to start RetroLog. Check the logs for more information."
    if command -v docker-compose &> /dev/null; then
        echo "   docker-compose logs"
    else
        echo "   docker compose logs"
    fi
    exit 1
fi
