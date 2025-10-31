# Peter Dashboard - Development CLI
# =====================================
# Convenient commands for local development

.PHONY: help
help: ## Show this help message
	@echo "Peter Dashboard - Development Commands"
	@echo "======================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# Docker Services
# =============================================================================

.PHONY: up
up: ## Start all services (postgres, redis, api, web)
	docker-compose up -d

.PHONY: down
down: ## Stop all services
	docker-compose down

.PHONY: restart
restart: down up ## Restart all services

.PHONY: logs
logs: ## Show logs from all services (follow mode)
	docker-compose logs -f

.PHONY: logs-api
logs-api: ## Show API logs only (follow mode)
	docker-compose logs -f api

.PHONY: logs-db
logs-db: ## Show database logs only (follow mode)
	docker-compose logs -f postgres

.PHONY: ps
ps: ## Show status of all services
	docker-compose ps

.PHONY: clean
clean: ## Stop and remove all containers, volumes, networks
	docker-compose down -v
	@echo "✓ All containers, volumes, and networks removed"

# =============================================================================
# Database Management
# =============================================================================

.PHONY: db-start
db-start: ## Start only postgres and redis
	docker-compose up -d postgres redis

.PHONY: db-stop
db-stop: ## Stop database services
	docker-compose stop postgres redis

.PHONY: db-shell
db-shell: ## Open psql shell in postgres container
	docker-compose exec postgres psql -U peter_user -d peter_db

.PHONY: db-migrate
db-migrate: ## Run database migrations (alembic upgrade head)
	cd apps/api && uv run alembic upgrade head

.PHONY: db-migrate-create
db-migrate-create: ## Create new migration (usage: make db-migrate-create MSG="description")
	@if [ -z "$(MSG)" ]; then \
		echo "Error: MSG is required. Usage: make db-migrate-create MSG='add users table'"; \
		exit 1; \
	fi
	cd apps/api && uv run alembic revision --autogenerate -m "$(MSG)"

.PHONY: db-rollback
db-rollback: ## Rollback last migration
	cd apps/api && uv run alembic downgrade -1

.PHONY: db-reset
db-reset: ## Drop all tables and re-run migrations (DESTRUCTIVE)
	@echo "⚠️  WARNING: This will DROP ALL TABLES and data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose exec postgres psql -U peter_user -d peter_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"; \
		cd apps/api && uv run alembic upgrade head; \
		echo "✓ Database reset complete"; \
	else \
		echo "Cancelled"; \
	fi

.PHONY: db-seed
db-seed: ## Seed database with sample data
	cd apps/api && uv run python scripts/seed_db.py

# =============================================================================
# API Development
# =============================================================================

.PHONY: api-start
api-start: db-start ## Start API locally (requires postgres+redis running)
	cd apps/api && uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: api-shell
api-shell: ## Open interactive Python shell with app context
	cd apps/api && uv run python scripts/shell.py

.PHONY: api-routes
api-routes: ## List all API routes
	cd apps/api && uv run python scripts/list_routes.py

.PHONY: api-health
api-health: ## Check API health endpoint
	@curl -s http://localhost:8000/health | python -m json.tool || echo "API not running"

# =============================================================================
# Testing
# =============================================================================

.PHONY: test
test: ## Run all tests
	cd apps/api && uv run pytest

.PHONY: test-unit
test-unit: ## Run unit tests only
	cd apps/api && uv run pytest tests/unit

.PHONY: test-integration
test-integration: ## Run integration tests only
	cd apps/api && uv run pytest tests/integration

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	cd apps/api && uv run pytest --cov=src --cov-report=html --cov-report=term

.PHONY: test-watch
test-watch: ## Run tests in watch mode (requires pytest-watch)
	cd apps/api && uv run ptw -- -v

# =============================================================================
# Code Quality
# =============================================================================

.PHONY: lint
lint: ## Run all linters (ruff + mypy)
	cd apps/api && uv run ruff check src tests
	cd apps/api && uv run mypy src

.PHONY: format
format: ## Format code with black and ruff
	cd apps/api && uv run black src tests
	cd apps/api && uv run ruff check --fix src tests

.PHONY: format-check
format-check: ## Check code formatting without changes
	cd apps/api && uv run black --check src tests
	cd apps/api && uv run ruff check src tests

.PHONY: typecheck
typecheck: ## Run type checking with mypy
	cd apps/api && uv run mypy src

# =============================================================================
# Dependencies
# =============================================================================

.PHONY: install
install: ## Install Python dependencies (uv)
	cd apps/api && uv sync

.PHONY: install-dev
install-dev: ## Install Python dev dependencies
	cd apps/api && uv sync --dev

.PHONY: update
update: ## Update Python dependencies
	cd apps/api && uv lock --upgrade

# =============================================================================
# Dashboard Management
# =============================================================================

.PHONY: dash-validate
dash-validate: ## Validate a dashboard YAML (usage: make dash-validate FILE=path/to/dash.yaml)
	@if [ -z "$(FILE)" ]; then \
		echo "Error: FILE is required. Usage: make dash-validate FILE=dashboards/revenue.yaml"; \
		exit 1; \
	fi
	cd apps/api && uv run python scripts/validate_dashboard.py $(FILE)

.PHONY: dash-list
dash-list: ## List all dashboards
	cd apps/api && uv run python scripts/list_dashboards.py

.PHONY: dash-precompute
dash-precompute: ## Precompute a dashboard (usage: make dash-precompute SLUG=revenue-dashboard)
	@if [ -z "$(SLUG)" ]; then \
		echo "Error: SLUG is required. Usage: make dash-precompute SLUG=revenue-dashboard"; \
		exit 1; \
	fi
	cd apps/api && uv run python scripts/precompute_dashboard.py $(SLUG)

# =============================================================================
# Cache Management
# =============================================================================

.PHONY: cache-flush
cache-flush: ## Flush all Redis cache
	docker-compose exec redis redis-cli FLUSHALL

.PHONY: cache-stats
cache-stats: ## Show Redis cache statistics
	docker-compose exec redis redis-cli INFO stats

# =============================================================================
# Development Utilities
# =============================================================================

.PHONY: shell-db
shell-db: db-shell ## Alias for db-shell

.PHONY: shell-api
shell-api: api-shell ## Alias for api-shell

.PHONY: shell-redis
shell-redis: ## Open redis-cli shell
	docker-compose exec redis redis-cli

.PHONY: build
build: ## Build all Docker images
	docker-compose build

.PHONY: build-api
build-api: ## Build API Docker image only
	docker-compose build api

# =============================================================================
# Full Stack Commands
# =============================================================================

.PHONY: dev
dev: ## Start full development environment (db + api)
	@echo "Starting development environment..."
	@make db-start
	@echo "Waiting for database..."
	@sleep 3
	@make db-migrate
	@echo "✓ Database ready"
	@echo "Starting API server..."
	@cd apps/api && uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: setup
setup: ## Initial setup (install deps + start services + migrate)
	@echo "🚀 Setting up Peter Dashboard..."
	@echo ""
	@echo "1/4 Installing Python dependencies..."
	@make install-dev
	@echo ""
	@echo "2/4 Starting database services..."
	@make db-start
	@echo ""
	@echo "3/4 Waiting for database to be ready..."
	@sleep 5
	@echo ""
	@echo "4/4 Running migrations..."
	@make db-migrate
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Quick start commands:"
	@echo "  make dev          - Start API server (local)"
	@echo "  make up           - Start all services (Docker)"
	@echo "  make test         - Run tests"
	@echo "  make help         - Show all commands"

.PHONY: teardown
teardown: ## Complete teardown (stop services + remove volumes)
	@echo "⚠️  Tearing down all services and data..."
	@make clean
	@echo "✓ Teardown complete"

# =============================================================================
# Frontend Development
# =============================================================================

.PHONY: web-install
web-install: ## Install frontend dependencies (pnpm)
	cd apps/web && pnpm install

.PHONY: web-dev
web-dev: ## Start frontend dev server
	cd apps/web && pnpm dev

.PHONY: web-build
web-build: ## Build frontend for production
	cd apps/web && pnpm build

.PHONY: web-start
web-start: ## Start production frontend server
	cd apps/web && pnpm start

.PHONY: web-lint
web-lint: ## Lint frontend code
	cd apps/web && pnpm lint

.PHONY: web-typecheck
web-typecheck: ## Type check frontend code
	cd apps/web && pnpm typecheck

.PHONY: web-test
web-test: ## Run frontend unit tests
	cd apps/web && pnpm test

.PHONY: web-test-e2e
web-test-e2e: ## Run frontend E2E tests
	cd apps/web && pnpm test:e2e

.PHONY: web-codegen
web-codegen: ## Generate TypeScript API client from OpenAPI spec
	cd packages/api-client && npx openapi-typescript-codegen --input ../../apps/api/src/openapi.yaml --output ./generated --client axios --useUnionTypes --exportSchemas true

.PHONY: web-clean
web-clean: ## Clean frontend build artifacts
	cd apps/web && rm -rf .next out

# =============================================================================
# Full Stack Development
# =============================================================================

.PHONY: dev-full
dev-full: ## Start full stack (api + web) in parallel
	@echo "Starting full stack development..."
	@make db-start
	@echo "Waiting for database..."
	@sleep 3
	@make db-migrate
	@echo "✓ Database ready"
	@echo "Starting API and Web servers..."
	@trap 'kill 0' EXIT; \
	(cd apps/api && uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload) & \
	(cd apps/web && pnpm dev)

.PHONY: setup-full
setup-full: ## Setup both backend and frontend
	@echo "🚀 Setting up Peter Dashboard (Full Stack)..."
	@echo ""
	@echo "Backend setup..."
	@make install-dev
	@make db-start
	@sleep 5
	@make db-migrate
	@echo ""
	@echo "Frontend setup..."
	@make web-install
	@make web-codegen
	@echo ""
	@echo "✅ Full stack setup complete!"
	@echo ""
	@echo "Quick start commands:"
	@echo "  make dev-full     - Start API + Web servers"
	@echo "  make web-dev      - Start Web server only"
	@echo "  make dev          - Start API server only"
	@echo "  make help         - Show all commands"

# =============================================================================
# CI/CD Simulation
# =============================================================================

.PHONY: ci
ci: format-check lint test ## Run backend CI checks (format, lint, test)

.PHONY: ci-full
ci-full: format-check lint test-cov ## Run full backend CI suite with coverage

.PHONY: ci-web
ci-web: web-lint web-typecheck web-build ## Run frontend CI checks (lint, typecheck, build)

.PHONY: ci-all
ci-all: ci ci-web ## Run CI checks for both backend and frontend
