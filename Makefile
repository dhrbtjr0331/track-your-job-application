MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
PROJECT_DIR := $(dir $(MAKEFILE_PATH))

.PHONY: help setup build start stop clean test lint

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Setup development environment
	@echo "Setting up development environment..."
	@chmod +x setup-dev.sh
	@./setup-dev.sh

build: ## Build all services
	@echo "Building all services..."
	@docker-compose build

start: ## Start all services
	@echo "Starting all services..."
	@docker-compose up -d

stop: ## Stop all services
	@echo "Stopping all services..."
	@docker-compose down

clean: ## Clean up containers, images, and volumes
	@echo "Cleaning up..."
	@docker-compose down -v --rmi all --remove-orphans

logs: ## Show logs from all services
	@docker-compose logs -f

backend-dev: ## Run backend in development mode
	@echo "Starting backend in development mode..."
	@cd backend && go run cmd/server/main.go

frontend-dev: ## Run frontend in development mode
	@echo "Starting frontend in development mode..."
	@cd frontend && npm run dev

agents-dev: ## Run agents in development mode
	@echo "Starting agents in development mode..."
	@cd agents && source venv/bin/activate && python main.py

test: ## Run tests for all services
	@echo "Running tests..."
	@cd backend && go test ./...
	@cd agents && source venv/bin/activate && pytest
	@cd frontend && npm test

lint: ## Run linters for all services
	@echo "Running linters..."
	@cd backend && go fmt ./...
	@cd frontend && npm run lint
	@cd agents && source venv/bin/activate && black . && flake8

install-deps: ## Install dependencies for all services
	@echo "Installing backend dependencies..."
	@cd backend && go mod tidy
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "Installing agent dependencies..."
	@cd agents && source venv/bin/activate && pip install -r requirements.txt

db-reset: ## Reset the database
	@echo "Resetting database..."
	@docker-compose down postgres
	@docker volume rm job-application-tracker_postgres_data || true
	@docker-compose up -d postgres

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -f http://localhost:8080/health || echo "Backend unhealthy"
	@curl -f http://localhost:8000/health || echo "Agents unhealthy"
	@curl -f http://localhost:3000 || echo "Frontend unhealthy"
