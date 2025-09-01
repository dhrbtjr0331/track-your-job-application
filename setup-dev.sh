# setup-dev.sh
#!/bin/bash

echo "🚀 Setting up Job Application Tracker Development Environment"

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking requirements..."
    
    command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }
    command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }
    command -v go >/dev/null 2>&1 || echo "⚠️  Go is not installed. Backend development won't work."
    command -v node >/dev/null 2>&1 || echo "⚠️  Node.js is not installed. Frontend development won't work."
    
    echo "✅ Requirements check completed"
}

# Setup environment
setup_environment() {
    echo "⚙️  Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📄 Created .env file from template"
        echo "⚠️  Please edit .env and add your API keys!"
    fi
    
    # Create necessary directories
    mkdir -p outputs
    mkdir -p credentials
    mkdir -p logs
    
    echo "📁 Created necessary directories"
}

# Setup Python agents
setup_agents() {
    echo "🐍 Setting up Python agents..."
    
    cd agents
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    echo "✅ Python agents setup completed"
    cd ..
}

# Setup Go backend (if Go is available)
setup_backend() {
    if command -v go >/dev/null 2>&1; then
        echo "🏗️  Setting up Go backend..."
        cd backend
        go mod tidy
        echo "✅ Go backend setup completed"
        cd ..
    else
        echo "⚠️  Skipping Go backend setup (Go not installed)"
    fi
}

# Setup React frontend (if Node is available)  
setup_frontend() {
    if command -v node >/dev/null 2>&1; then
        echo "⚛️  Setting up React frontend..."
        cd frontend
        npm install
        echo "✅ React frontend setup completed"
        cd ..
    else
        echo "⚠️  Skipping React frontend setup (Node.js not installed)"
    fi
}

# Setup Docker services
setup_docker() {
    echo "🐳 Setting up Docker services..."
    
    # Start databases
    docker-compose up -d postgres redis
    
    # Wait for databases to be ready
    echo "⏳ Waiting for databases to be ready..."
    sleep 10
    
    echo "✅ Docker services setup completed"
}

# Main setup flow
main() {
    check_requirements
    setup_environment
    setup_agents
    setup_backend
    setup_frontend
    setup_docker
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit .env file and add your API keys"
    echo "2. Add Gmail credentials to credentials/ directory"
    echo "3. Start the agents service: make agents-dev"
    echo "4. Test the setup: curl http://localhost:8000/health"
    echo ""
    echo "📚 Available commands:"
    echo "  make help     - Show all available commands"
    echo "  make start    - Start all services"
    echo "  make logs     - View service logs"
    echo ""
    echo "Happy coding! 🚀"
}

main
