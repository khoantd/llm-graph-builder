#!/bin/bash

# LLM Graph Builder Backend Docker Runner
# This script helps you run the backend container with proper configuration

echo "🚀 Starting LLM Graph Builder Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create a .env file based on example.env"
    echo "   cp example.env .env"
    echo "   Then edit .env with your configuration"
    exit 1
fi

# Default port
PORT=${PORT:-8000}

# Run the container
echo "🔧 Running backend container on port $PORT..."
echo "📋 Container will be accessible at: http://localhost:$PORT"
echo "📖 API docs will be available at: http://localhost:$PORT/docs"
echo ""
echo "Press Ctrl+C to stop the container"
echo ""

docker run -it --rm \
    --name llm-graph-builder-backend \
    -p $PORT:8000 \
    --env-file .env \
    llm-graph-builder-backend
