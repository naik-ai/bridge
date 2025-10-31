# Dev Server Skill

**Purpose**: Quickly start, stop, monitor, and debug all services (backend API, frontend web app, Redis, Postgres) during local development.

## When to Use This Skill

Use this skill when:
- Starting work session (spin up all services)
- Debugging issues (check logs, health status)
- Testing integrations (ensure all dependencies running)
- Switching branches (restart with fresh state)
- Troubleshooting errors (tail logs in real-time)

## Critical Commands for MVP

### 1. Start All Services

```bash
# Start everything (backend + frontend + dependencies)
python scripts/dev.py start --all

# Start specific service
python scripts/dev.py start --service=api
python scripts/dev.py start --service=web
```

**What it does**:
- Starts Postgres (port 5432)
- Starts Redis (port 6379)
- Starts FastAPI backend (port 8000)
- Starts Next.js frontend (port 3000)
- Runs migrations automatically
- Seeds test data (if `--seed` flag provided)

**Output example**:
```
✅ Postgres running on localhost:5432
✅ Redis running on localhost:6379
⏳ Running migrations...
✅ Migrations applied (3 pending → 0 pending)
✅ API running on http://localhost:8000
✅ Web running on http://localhost:3000

🎉 All services ready!
Open http://localhost:3000 to start developing.
```

### 2. Check Logs

```bash
# Tail all logs (live updates)
python scripts/dev.py logs --follow

# View logs for specific service
python scripts/dev.py logs --service=api --follow
python scripts/dev.py logs --service=web --tail=100

# Filter logs by level
python scripts/dev.py logs --level=error
```

**What it does**:
- Shows JSON-formatted logs from all services
- Highlights errors in red, warnings in yellow
- Includes correlation IDs for tracing requests
- Auto-scrolls with `--follow`

**Output example**:
```json
{"timestamp": "2025-10-29T10:15:23Z", "level": "info", "service": "api", "event": "trip_created", "user_id": "...", "trip_id": "...", "correlation_id": "abc-123"}
{"timestamp": "2025-10-29T10:15:24Z", "level": "error", "service": "api", "event": "llm_request_failed", "error": "Rate limit exceeded", "correlation_id": "abc-123"}
```

### 3. Health Check

```bash
# Check health of all services
python scripts/dev.py health

# Check specific service
python scripts/dev.py health --service=api
```

**What it does**:
- Pings `/health` endpoints for all services
- Checks database connectivity
- Verifies Redis connection
- Shows version info, uptime

**Output example**:
```
Service    Status    Uptime    Version
─────────────────────────────────────
postgres   ✅ UP     2h 15m    16.2
redis      ✅ UP     2h 15m    7.2.4
api        ✅ UP     1h 30m    0.1.0
web        ✅ UP     1h 30m    0.1.0

🎉 All services healthy!
```

### 4. Stop Services

```bash
# Stop all services
python scripts/dev.py stop --all

# Stop specific service
python scripts/dev.py stop --service=api
```

### 5. Restart Services

```bash
# Restart all (useful after config changes)
python scripts/dev.py restart --all

# Restart specific service
python scripts/dev.py restart --service=api
```

## Integration with Agents

### Backend Agent Workflow

When backend-agent makes changes:

```bash
# 1. Make changes to FastAPI code
# Edit apps/api/src/api/v1/trips.py

# 2. Restart API to apply changes
python scripts/dev.py restart --service=api

# 3. Check logs for errors
python scripts/dev.py logs --service=api --follow

# 4. Verify health
python scripts/dev.py health --service=api
```

**Database migration workflow**:

```bash
# 1. Create migration
cd apps/api
alembic revision --autogenerate -m "Add trip_members table"

# 2. Apply migration (dev server does this automatically on restart)
python scripts/dev.py restart --service=api
# Or manually:
alembic upgrade head

# 3. Verify migration applied
python scripts/dev.py health --service=api
# Should show: "Migrations: 0 pending"
```

### Frontend Agent Workflow

When frontend-agent makes changes:

```bash
# 1. Make changes to Next.js components
# Edit apps/web/app/trips/page.tsx

# 2. Next.js auto-reloads (no restart needed)
# But if environment variables changed:
python scripts/dev.py restart --service=web

# 3. Check for build errors
python scripts/dev.py logs --service=web --level=error

# 4. Verify page loads
curl http://localhost:3000/app/trips
```

### Integration Agent Workflow

When integration-agent runs E2E tests:

```bash
# 1. Ensure all services running
python scripts/dev.py health
# If any down:
python scripts/dev.py start --all

# 2. Seed test data
python scripts/dev.py start --all --seed

# 3. Run E2E tests
pnpm run test:e2e

# 4. Check logs for test failures
python scripts/dev.py logs --service=api --filter="test_user"
```

## MVP Workflow Examples

### Week 1: Initial Setup

```bash
# First time setup
# 1. Install dependencies
pnpm install
pip install -r apps/api/requirements.txt

# 2. Start all services (will create DB, run migrations)
python scripts/dev.py start --all --seed

# 3. Verify everything running
python scripts/dev.py health

# 4. Open browser
open http://localhost:3000
```

### Week 2: Daily Development

```bash
# Morning: Start work session
python scripts/dev.py start --all

# During development: Monitor logs
python scripts/dev.py logs --follow

# After backend change: Restart API
python scripts/dev.py restart --service=api

# Debugging: Check specific service health
python scripts/dev.py health --service=api

# End of day: Stop services (or leave running)
python scripts/dev.py stop --all
```

### Week 3: Testing LLM Streaming

```bash
# 1. Start services with seed data
python scripts/dev.py start --all --seed

# 2. Tail API logs to see LLM requests
python scripts/dev.py logs --service=api --filter="llm" --follow

# 3. In browser: Send chat message in trip

# 4. Watch logs for:
#    - LLM request sent
#    - Token streaming events
#    - Cost tracking events
#    - Cache hits/misses

# Example log output:
# {"event": "llm_request_start", "model": "claude", "tokens_estimated": 150}
# {"event": "llm_token_received", "chunk": "Sure! For Bali..."}
# {"event": "cost_event_logged", "cost_usd": 0.0045, "tokens": 150}
# {"event": "cache_miss", "key": "claude:..."}
```

## Environment Management

The dev server reads configuration from:

```bash
# .env.local (create from .env.example)
DATABASE_URL=postgresql://localhost:5432/antirush_dev
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Start with custom env file
python scripts/dev.py start --all --env=.env.test
```

## Port Configuration

Default ports (can be changed in `scripts/dev.py`):

| Service  | Port | URL |
|----------|------|-----|
| Postgres | 5432 | N/A (database) |
| Redis    | 6379 | N/A (cache) |
| API      | 8000 | http://localhost:8000 |
| Web      | 3000 | http://localhost:3000 |

## Troubleshooting

### Problem: "Port 8000 already in use"

```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use dev script
python scripts/dev.py stop --service=api
python scripts/dev.py start --service=api
```

### Problem: "Database connection failed"

```bash
# Check if Postgres running
python scripts/dev.py health --service=postgres

# If down, restart
python scripts/dev.py restart --service=postgres

# Check migrations
cd apps/api
alembic current  # Should show latest revision
alembic upgrade head  # Apply pending migrations
```

### Problem: "Redis connection timeout"

```bash
# Check Redis health
python scripts/dev.py health --service=redis

# If down, restart
python scripts/dev.py restart --service=redis

# Test connection manually
redis-cli ping
# Should return: PONG
```

### Problem: "Migration conflicts"

```bash
# Reset database (DESTRUCTIVE - dev only!)
python scripts/dev.py reset --database

# This will:
# 1. Drop all tables
# 2. Run all migrations from scratch
# 3. Seed test data
```

## File Ownership

This skill manages:

```
/
├── scripts/dev.py                  # Dev server orchestration
├── .env.local                      # Local environment variables
├── apps/api/
│   ├── migrations/                 # Alembic migrations
│   └── src/main.py                 # FastAPI app entry point
└── apps/web/
    └── next.config.js              # Next.js configuration
```

## Testing Checklist

- [ ] All services start successfully (`python scripts/dev.py start --all`)
- [ ] Health checks pass (`python scripts/dev.py health`)
- [ ] Logs visible for all services (`python scripts/dev.py logs --follow`)
- [ ] Hot reload works (change code → auto-restart)
- [ ] Migrations apply automatically on startup
- [ ] Seed data loads correctly (`--seed` flag)
- [ ] Services stop cleanly (`python scripts/dev.py stop --all`)

## Advanced Usage

### Running in Docker (Optional)

```bash
# Start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop
docker-compose down
```

### Background Mode

```bash
# Start services in background (detached)
python scripts/dev.py start --all --detach

# Check status
python scripts/dev.py health

# Tail logs later
python scripts/dev.py logs --follow
```

### Custom Service Combinations

```bash
# Only backend stack (no frontend)
python scripts/dev.py start postgres redis api

# Only frontend (assumes backend running elsewhere)
python scripts/dev.py start web
```

## References

- **Backend PDR**: `docs-pdr/backend_pdr.md` (§13 - Local dev setup)
- **Frontend PDR**: `docs-pdr/frontend_pdr.md` (Next.js dev server)
- **Scripts**: `scripts/dev.py` (implementation)

## Activation Triggers

Use this skill when you see:
- "start the server"
- "run locally"
- "check logs"
- "debug issue"
- "services not running"
- "restart backend"
- "health check"
