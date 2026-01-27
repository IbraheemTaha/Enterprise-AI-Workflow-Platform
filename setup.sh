#!/bin/bash

echo "🚀 Setting up Enterprise AI Workflow Platform..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose not found."
    exit 1
fi

# Check .env exists
if [ ! -f .env ]; then
    echo "✅ .env file exists"
    echo "⚠️  Make sure to edit .env and add your API keys!"
else
    echo "✅ .env file found"
fi

# Create directories
mkdir -p services/airflow/{dags,logs,plugins}
mkdir -p data

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Add your API keys (OpenAI, Anthropic, Google, or AWS)"
echo "3. Run: make start"
