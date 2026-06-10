.PHONY: help install dev build test lint migrate docker-up docker-down \
        seed backup restore monitor format typecheck clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	pip install --upgrade pip setuptools wheel
	pip install -r backend/requirements.txt -r backend/requirements-dev.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm ci

dev: ## Start development environment
	@echo "Starting development services..."
	docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up -d
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Docs: http://localhost:8000/docs"

build: ## Build Docker images
	docker build -t reminderbot-backend:latest backend/
	docker build -t reminderbot-frontend:latest frontend/

test: ## Run tests
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing
	@echo "Running frontend tests..."
	cd frontend && npm run test -- --coverage

lint: ## Run all linters
	@echo "Linting Python..."
	ruff check backend/
	black --check backend/
	isort --check-only backend/
	mypy backend/ --ignore-missing-imports
	@echo "Linting TypeScript..."
	cd frontend && npm run lint
	cd frontend && npx prettier --check "src/**/*.{ts,tsx,js,jsx,json}"

format: ## Format code
	@echo "Formatting Python..."
	ruff check backend/ --fix
	black backend/
	isort backend/
	@echo "Formatting TypeScript..."
	cd frontend && npx prettier --write "src/**/*.{ts,tsx,js,jsx,json}"

typecheck: ## Run type checks
	mypy backend/ --ignore-missing-imports
	cd frontend && npm run typecheck

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-new: ## Create new migration (usage: make migrate-new msg="description")
	cd backend && alembic revision --autogenerate -m "$(msg)"

docker-up: ## Start Docker Compose stack
	docker compose -f infra/docker/docker-compose.yml up -d
	@echo "Stack started. Check health with: make healthcheck"

docker-down: ## Stop Docker Compose stack
	docker compose -f infra/docker/docker-compose.yml down

docker-logs: ## Tail Docker logs
	docker compose -f infra/docker/docker-compose.yml logs -f

seed: ## Seed default data
	cd backend && python -m scripts.seed

backup: ## Backup database
	./scripts/backup.sh

restore: ## Restore database (usage: make restore FILE=backups/file.sql.gz)
	./scripts/restore.sh $(FILE)

healthcheck: ## Run health checks
	./scripts/healthcheck.sh

monitor: ## Run monitoring checks
	./scripts/monitor.sh

setup: ## Run full setup script
	./scripts/setup.sh

clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete."
