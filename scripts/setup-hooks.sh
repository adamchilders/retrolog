#!/bin/bash

# Setup script for Git hooks
# This script configures pre-commit hooks for the RetroLog project

echo "🔧 Setting up Git hooks for RetroLog..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a Git repository. Please run this from the project root."
    exit 1
fi

# Set the hooks path
git config core.hooksPath .githooks

# Make sure hook files are executable
chmod +x .githooks/pre-commit
chmod +x scripts/pre-commit.sh

echo "✅ Git hooks configured successfully!"
echo ""
echo "📋 What this means:"
echo "   • Tests will run automatically before each commit"
echo "   • Commits will be blocked if tests fail"
echo "   • Sensitive data checks will prevent accidental commits of API keys"
echo ""
echo "🚀 To test the setup, try making a commit:"
echo "   git add ."
echo "   git commit -m 'test commit'"
echo ""
echo "💡 To bypass hooks in emergencies (not recommended):"
echo "   git commit --no-verify -m 'emergency commit'"
