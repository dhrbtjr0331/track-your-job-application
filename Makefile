# Makefile
.PHONY: help setup start stop logs test lint clean health

# Default target
help:
	@echo "Available commands:"
	@echo "  setup     - Complete development setup"
	@echo "  start     - Start all services with Docker"
	@echo "  stop      - Stop all services"
	@echo "  logs      - View service logs"
	@echo "  test      - Run all tests"
	@echo "  lint      - Run all linters"
	@echo "  clean     - Clean up Docker resources"
	@echo "  health    - Check service health"
	@echo "  agents-dev - Run agents in development mode"

# Complete setup
setup: 
	@echo "Setting up Job Application Tracker..."
	@chmod +x setup-dev.sh
	@./setup-dev.sh

# Docker operations
start:
	docker-compose up -d postgres redis agents

start-all:
	docker-compose --profile frontend --profile backend up -d

stop:
	docker-compose down

logs:
	docker-compose logs -f

# Development
agents-dev:
	cd agents && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py

backend-dev:
	cd backend && go mod tidy && go run cmd/server/main.go

frontend-dev:
	cd frontend && npm install && npm run dev

# Testing and quality
test:
	@echo "Running tests..."
	cd agents && python -m pytest tests/ -v
	cd backend && go test ./...
	cd frontend && npm test

lint:
	@echo "Running linters..."
	cd agents && flake8 src/ --max-line-length=100
	cd backend && golangci-lint run
	cd frontend && npm run lint

# Maintenance
clean:
	docker-compose down -v
	docker system prune -f

db-reset:
	docker-compose down postgres
	docker volume rm jobtracker_postgres_data
	docker-compose up -d postgres

health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "Agents service down"
	@curl -f http://localhost:8080/health || echo "Backend service down"
	@curl -f http://localhost:3000 || echo "Frontend service down"
