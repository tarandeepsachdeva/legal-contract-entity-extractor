#!/bin/bash
# Docker Deployment Script for Legal NER API

echo "🐳 DEPLOYING LEGAL NER API WITH DOCKER"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    echo "📱 Open Docker Desktop application from Applications folder"
    exit 1
fi

echo "✅ Docker is running!"

# Build Docker image
echo "🏗️ Building Docker image..."
docker build -t legal-ner-api .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
else
    echo "❌ Docker image build failed!"
    exit 1
fi

# Run Docker container
echo "🚀 Starting Docker container..."
docker run -d \
    -p 5001:5001 \
    --name legal-ner-api \
    --restart unless-stopped \
    legal-ner-api

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully!"
    echo "🌐 API is running at: http://localhost:5001"
    echo ""
    echo "🧪 Test the API:"
    echo "curl http://localhost:5001/health"
    echo ""
    echo "📊 Test entity extraction:"
    echo 'curl -X POST http://localhost:5001/extract -H "Content-Type: application/json" -d '"{"text": "loan agreement for \$100,000"}"'
    echo ""
    echo "🛑 To stop: docker stop legal-ner-api"
    echo "🗑️  To remove: docker rm legal-ner-api"
    echo "📋 To view logs: docker logs legal-ner-api"
else
    echo "❌ Container failed to start!"
    exit 1
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "🌐 Your Legal NER API is now running at http://localhost:5001"
