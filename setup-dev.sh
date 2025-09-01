#!/bin/bash

# Job Application Tracker - Development Setup Script

set -e

echo "🚀 Setting up Job Application Tracker development environment..."

# Check if required tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install $1 and try again."
        exit 1
    else
        echo "✅ $1 is installed"
    fi
}

echo "🔍 Checking required tools..."
check_tool "go"
check_tool "python3"
check_tool "node"
check_tool "docker"
check_tool "docker-compose"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual API keys and configuration"
else
    echo "✅ .env file already exists"
fi

# Setup backend
echo "🔧 Setting up Go backend..."
cd backend
if [ ! -f go.sum ]; then
    go mod tidy
fi
cd ..

# Setup frontend
echo "🎨 Setting up React frontend..."
cd frontend
if [ ! -d node_modules ]; then
    npm install
fi
cd ..

# Setup agents
echo "🤖 Setting up Python agents..."
cd agents
if [ ! -d venv ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p outputs/excel
mkdir -p outputs/logs
mkdir -p outputs/exports
mkdir -p credentials

# Database setup
echo "🗄️ Setting up database..."
docker-compose up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit the .env file with your API keys"
echo "2. Add Gmail API credentials to credentials/gmail_credentials.json"
echo "3. Run 'docker-compose up -d' to start all services"
echo "4. Or run individual services:"
echo "   - Backend: cd backend && go run cmd/server/main.go"
echo "   - Frontend: cd frontend && npm run dev"
echo "   - Agents: cd agents && source venv/bin/activate && python main.py"
echo ""
echo "🌐 Application will be available at:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend: http://localhost:8080"
echo "   - Agents: http://localhost:8000"
