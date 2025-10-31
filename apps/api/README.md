# Peter API - FastAPI Backend

FastAPI backend service for the Peter dashboard platform. Handles dashboard management, BigQuery query execution, authentication, caching, and lineage tracking.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- PostgreSQL 14+
- Redis 7+ (optional for MVP)
- Google Cloud Project with BigQuery and Cloud Storage

## Quick Start

### Recommended: Use Makefile Commands

From the project root (`/bridge`):

```bash
# First time setup (installs deps, starts DB, runs migrations)
make setup

# Start development server (fast reload)
make dev
```

The API will be available at `http://localhost:8000`
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

**📖 See [CLI Guide](../../docs/cli_guide.md) for complete command reference**
**⚡ See [Quick Reference](../../docs/cli_quick_reference.md) for daily commands**

### Alternative: Manual Setup with uv

<details>
<summary>Click to expand manual setup instructions</summary>

#### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

#### 2. Setup Project

```bash
cd apps/api

# Install dependencies
uv sync --dev
```

#### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Minimum required:
# - DATABASE_URL
# - GCP_PROJECT_ID
# - BIGQUERY_DATASET
# - GOOGLE_OAUTH_CLIENT_ID/SECRET
# - ALLOWED_EMAILS
```

#### 4. Initialize Database

```bash
# Run migrations
uv run alembic upgrade head
```

#### 5. Run Development Server

```bash
# Using uv run (no need to activate venv)
uv run uvicorn src.main:app --reload --port 8000
```

</details>

## Development Workflow

### Adding Dependencies

```bash
# Add production dependency
uv pip install <package-name>

# Add dev dependency
uv pip install --dev <package-name>

# Or edit pyproject.toml and sync
uv pip sync
```

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test file
uv run pytest tests/unit/test_validator.py -v

# Integration tests only
uv run pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint
uv run ruff check src/ tests/

# Type checking
uv run mypy src/

# Run all checks
uv run black src/ tests/ && uv run ruff check src/ tests/ && uv run mypy src/
```

### Database Migrations

```bash
# Create new migration (auto-generate from models)
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Show current revision
uv run alembic current

# Show migration history
uv run alembic history
```

## Docker Development

### Using Docker Compose

```bash
# Start all services (API, Postgres, Redis)
docker-compose up

# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Database Shell

```bash
# PostgreSQL shell
docker-compose exec postgres psql -U peter -d peter_db

# Redis CLI
docker-compose exec redis redis-cli
```

## Project Structure

```
apps/api/
├── src/
│   ├── api/              # API route handlers
│   │   ├── auth.py
│   │   ├── dashboards.py
│   │   ├── data.py
│   │   ├── health.py
│   │   ├── lineage.py
│   │   └── sql.py
│   ├── core/             # Core configuration and dependencies
│   │   ├── auth.py       # Authentication logic
│   │   ├── cache.py      # Cache interface and implementations
│   │   ├── config.py     # Settings and configuration
│   │   ├── dependencies.py # FastAPI dependencies
│   │   ├── logging_config.py # Structured logging
│   │   ├── secrets.py    # Secret Manager integration
│   │   └── telemetry.py  # OpenTelemetry setup
│   ├── db/               # Database and migrations
│   │   ├── base.py       # SQLAlchemy base
│   │   └── database.py   # Database connection
│   ├── integrations/     # External service integrations
│   │   ├── bigquery_client.py # BigQuery wrapper
│   │   ├── gcs_storage.py     # GCS storage backend
│   │   └── storage_interface.py # Storage abstraction
│   ├── models/           # Data models
│   │   ├── dashboard_schema.py # Pydantic models for YAML
│   │   ├── db_models.py        # SQLAlchemy ORM models
│   │   └── api_models.py       # Request/response models
│   ├── services/         # Business logic services
│   │   ├── compiler.py         # Dashboard compiler
│   │   ├── dashboard_service.py # Dashboard management
│   │   ├── lineage_service.py  # Lineage tracking
│   │   ├── query_executor.py   # SQL execution
│   │   ├── session_service.py  # Session management
│   │   ├── validator.py        # YAML validation
│   │   └── verification_builder.py # LLM verification payloads
│   ├── utils/            # Utilities and helpers
│   │   ├── cache_keys.py
│   │   ├── sql_parser.py
│   │   └── transformers.py
│   ├── main.py           # FastAPI application entry
│   └── __init__.py
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── api/              # API endpoint tests
│   ├── e2e/              # End-to-end tests
│   ├── performance/      # Performance/load tests
│   └── conftest.py       # Pytest fixtures
├── alembic/              # Database migrations
├── scripts/              # Utility scripts
├── examples/             # Example dashboards
├── .env.example          # Environment variables template
├── .gitignore
├── docker-compose.yml    # Local development environment
├── Dockerfile            # Production container
├── pyproject.toml        # Project configuration and dependencies
└── README.md
```

## API Endpoints

### Authentication
- `GET /api/v1/auth/login` - Initiate OAuth flow
- `GET /api/v1/auth/callback` - OAuth callback
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Current user info

### Dashboards
- `POST /api/v1/dashboards/validate` - Validate YAML
- `POST /api/v1/dashboards/compile` - Compile to execution plan
- `POST /api/v1/dashboards` - Create dashboard
- `GET /api/v1/dashboards` - List dashboards
- `GET /api/v1/dashboards/{slug}` - Get dashboard
- `PUT /api/v1/dashboards/{slug}` - Update dashboard
- `DELETE /api/v1/dashboards/{slug}` - Delete dashboard

### SQL Execution
- `POST /api/v1/sql/run` - Execute SQL (verification)
- `POST /api/v1/sql/validate` - Validate SQL syntax
- `POST /api/v1/sql/explain` - Get query execution plan

### Data Serving
- `GET /api/v1/dashboards/{slug}/data` - Get dashboard data
- `GET /api/v1/dashboards/{slug}/charts/{chart_id}/data` - Get chart data
- `GET /api/v1/dashboards/{slug}/freshness` - Get data freshness

### Cache Management
- `POST /api/v1/dashboards/{slug}/precompute` - Warm cache
- `DELETE /api/v1/cache` - Invalidate cache
- `GET /api/v1/cache/stats` - Cache statistics

### Lineage & Analytics
- `GET /api/v1/dashboards/{slug}/lineage` - Get lineage graph
- `GET /api/v1/lineage/upstream/{node_id}` - Get upstream dependencies
- `GET /api/v1/analytics/costs` - Query cost analytics

### Health
- `GET /health` - Health check
- `GET /ready` - Readiness probe

## Environment Variables

See `.env.example` for all available configuration options.

### Required Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/peter_db

# GCP
GCP_PROJECT_ID=my-project
BIGQUERY_DATASET=analytics

# Auth
GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=xxx
ALLOWED_EMAILS=user1@example.com,user2@example.com

# Session
SESSION_SECRET_KEY=generate-random-key-for-production
```

## Testing

### Unit Tests

Test individual components in isolation:

```bash
uv run pytest tests/unit/ -v
```

### Integration Tests

Test integration with external services (requires test GCP project):

```bash
# Set test environment
export TESTING=true
export TEST_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/peter_test_db

uv run pytest tests/integration/ -v
```

### API Tests

Test HTTP endpoints:

```bash
uv run pytest tests/api/ -v
```

### Performance Tests

Run load tests:

```bash
# Start Locust
uv run locust -f tests/performance/locustfile.py

# Or run headless
uv run locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 5m
```

## Deployment

### Cloud Run Deployment

```bash
# Build image
docker build -t gcr.io/PROJECT_ID/peter-api:latest .

# Push to Google Container Registry
docker push gcr.io/PROJECT_ID/peter-api:latest

# Deploy to Cloud Run
gcloud run deploy peter-api \
  --image gcr.io/PROJECT_ID/peter-api:latest \
  --region us-central1 \
  --platform managed \
  --memory 1Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars APP_ENV=production \
  --set-secrets DATABASE_URL=DATABASE_URL:latest,SESSION_SECRET_KEY=SESSION_SECRET_KEY:latest
```

See `docs/deployment.md` for detailed deployment instructions.

## Troubleshooting

### Common Issues

**uv not found**:
```bash
# Ensure uv is in PATH
which uv

# Reinstall if needed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Import errors**:
```bash
# Ensure you're in the virtual environment
source .venv/bin/activate

# Reinstall in editable mode
uv pip install -e .
```

**Database connection errors**:
```bash
# Check Postgres is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

**BigQuery authentication errors**:
```bash
# Check service account has permissions
gcloud projects get-iam-policy $GCP_PROJECT_ID

# Set application default credentials for local dev
gcloud auth application-default login
```

## Performance Benchmarks

Target performance (PDR requirements):

- **Cached dashboard load**: p95 < 300ms
- **Cold dashboard load**: p95 < 1.5s
- **SQL verification**: p95 < 2s (<1GB scans)
- **Concurrent requests**: 100+ without degradation

Run benchmarks:

```bash
uv run pytest tests/performance/ -v --benchmark
```

## Contributing

1. Create feature branch
2. Make changes
3. Run tests and linting: `uv run pytest && uv run black . && uv run ruff check .`
4. Submit PR

## License

Proprietary - Internal use only

## Support

For issues or questions, see project documentation or contact the team.
