# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Peter** (named after Peter Lynch) is an LLM-assisted dashboard platform that enables users to create, edit, and monitor data visualizations through natural language and YAML definitions. The system pushes all heavy computation to BigQuery while providing a clean, minimal interface for dashboard authoring and exploration.

**Core Philosophy**: Dashboards-as-code with YAML as the single source of truth. LLM agents assist in SQL generation and verification. All analytical queries execute in BigQuery; backend serves compact, cache-first results.

**Target**: MVP completion in 3 weeks for ~10 initial users.

---

## Architecture

### System Components

1. **Backend** (`apps/api/`): FastAPI service deployed to Cloud Run
   - REST API for dashboard lifecycle, SQL verification, data serving
   - Postgres for operational metadata (users, sessions, dashboard indices)
   - Redis/in-process cache for precomputed chart payloads
   - BigQuery for all analytical queries (with result cache and byte caps)
   - OpenTelemetry instrumentation for observability

2. **Frontend** (`apps/web/`): Next.js 15 App Router application
   - Three-panel VS Code-inspired layout: Explorer | Workspace | Assistant
   - ShadCN/UI design system (monotone black/white/grey theme)
   - Recharts for visualizations
   - Three view types: Analytical, Operational, Strategic
   - Server-side auth with Google SSO

3. **Data Layer**:
   - YAML files as source of truth (Git-style storage or GCS)
   - Postgres stores pointers/indices, not content
   - BigQuery executes all queries with guardrails (max bytes billed, result cache)
   - Lineage graph tracks dashboard → charts → queries → tables

### Key Patterns

- **Git-based YAML storage**: Dashboards stored as YAML in `/dashboards/` directory, Git provides version control
- **Two-way sync**: UI → YAML (automatic on save), YAML → UI (filesystem read on request)
- **Explicit precompute model**: No automatic refresh in MVP. Manual trigger warms cache.
- **LLM verification loop**: Agent proposes SQL → backend executes with limits → returns metadata + sample (≤100 rows) → agent validates → iterate or finalize
- **Dirty state tracking**: No autosave; explicit Save workflow with confirmation dialogs
- **Compact payloads**: Backend transforms BigQuery results to visualization-ready JSON (target: <100 KB per chart)

### Architectural Principles (Backend)

1. **Three-Layer Architecture**:
   - API Layer: Thin endpoints (`/src/api/v1/`) with request/response models only
   - Service Layer: All business logic (`/src/services/`) with validation, orchestration
   - Database Layer: SQLModel ORM models (`/src/models/db_models.py`), engine, sessions

2. **Separate API Models from DB Models**:
   - DB models: Database schema definition (SSOT for table structure)
   - API models: Response enrichment with computed fields, user data, type conversions
   - Pattern: `DashboardResponse.from_db_model(db_dashboard, owner=user, chart_count=n)`
   - Benefits: API evolves independently, Decimal→string conversions, enriched responses

3. **Service Layer Pattern**:
   - Constructor injection: `__init__(self, db: AsyncSession)`
   - All business logic in services, never in endpoints
   - Dedicated validators: `DashboardValidator`, `YAMLValidator` classes
   - Bulk operations: Single method handles 1-N items with optimized DB operations

4. **Universal Bulk Operations**:
   - Single endpoint for any quantity: `PUT /items` handles 1 to 1000 items
   - Convenience wrapper: `PUT /items/{id}` delegates to bulk endpoint
   - Performance: Uses `bulk_update_mappings()` for N items in single transaction
   - Consistency: Same business logic applied whether 1 or 1000 items

5. **Response Factory Pattern**:
   - Standard envelope: `{success: bool, data: T, error: APIError, metadata: {...}}`
   - Factory methods: `ResponseFactory.success(data)` / `ResponseFactory.error(code, msg)`
   - Automatic injection: timestamp, request_id, version
   - Enum error codes: Prevent typos, enable i18n

6. **Optimized Database Queries**:
   - Window functions: `func.count().over().label("total_count")` - 1 query not 2
   - JOIN enrichment: Include user/metadata in single query, no N+1
   - Bulk operations: `bulk_update_mappings()` for updates, `bulk_insert_mappings()` for inserts
   - Type safety: All queries properly typed with AsyncSession

7. **Type Safety Throughout**:
   - Function signatures: Full annotations for params + return types
   - Pydantic models: Field validators for complex logic
   - Generic types: `APIResponse[T]` for reusable patterns
   - UUID not string: All IDs use UUID type

8. **Dependency Injection**:
   - Service factories: `get_dashboard_service(db: AsyncSession = Depends(...))`
   - Auth composability: `require_editor()` builds on `get_current_user()`
   - Testability: Override dependencies in tests
   - Clean signatures: Endpoints receive services, not DB sessions

9. **Validation Separation**:
   - Validator classes: Encapsulate validation logic
   - Sync first: Run cheap validations before expensive async ones
   - Database-aware: Can validate uniqueness, existence constraints
   - Composable: Small methods combined for comprehensive validation

10. **Async All The Way**:
    - Endpoints: `async def endpoint(...)`
    - Services: All methods async
    - Database: AsyncSession, async queries
    - Typing: AsyncGenerator for dependencies

---

## Design System & Visual Theme

### Monotone Color Palette

**CRITICAL**: This project uses a strict **black/white/grey monotone theme**. Minimize color usage.

```
Background Tones:
- bg-primary: #FFFFFF (light mode) / #0A0A0A (dark mode)
- bg-secondary: #F9F9F9 (light) / #171717 (dark)
- bg-tertiary: #F3F3F3 (light) / #262626 (dark)

Text Tones:
- text-primary: #0A0A0A (light) / #FAFAFA (dark)
- text-secondary: #525252 (light/dark)
- text-tertiary: #737373 (light/dark)

Border/Divider:
- border: #E5E5E5 (light) / #404040 (dark)

Accent (minimal use):
- Selection/Focus: #0A0A0A (light) / #FAFAFA (dark)
- Hover: subtle opacity shift (90% → 100%)
```

**Color Usage Rules**:
- **NO branded colors** (no blues, greens, reds for UI elements)
- Use semantic colors ONLY for data/status:
  - Success: subtle green (#10B981) - only for status indicators
  - Warning: subtle yellow (#F59E0B) - only for alerts
  - Error: subtle red (#EF4444) - only for errors
  - Neutral: grey for data that has no sentiment
- Charts use **greyscale gradients** as default; semantic colors only when explicitly needed for data meaning
- Focus rings: 2px solid black (light mode) or white (dark mode)

### Typography

```
Font Family: Inter (system fallback: -apple-system, sans-serif)

Headings:
- h1: 32px / 600 weight
- h2: 24px / 600 weight
- h3: 20px / 600 weight
- h4: 16px / 600 weight

Body:
- Default: 16px / 400 weight
- Small: 14px / 400 weight
- Tiny: 12px / 400 weight

Numeric/Data:
- KPI value: 28-32px / 600 weight / tabular-nums
- Chart label: 12px / 400 weight
- Table cell: 14px / 400 weight / tabular-nums
```

### Spacing & Layout

- **12-column responsive grid**
- Gutters: 16px (mobile), 24px (desktop)
- Spacing scale: 4px, 8px, 16px, 24px, 32px, 48px
- Max content width: 1440px
- Border radius: 4px (inputs), 8px (cards), 12px (modals)

### Component Library

- **Base**: ShadCN/UI components (buttons, cards, inputs, dropdowns, dialogs)
- **Charts**: Recharts wrapped in ShadCN chart containers
- **Icons**: Lucide icons (minimal, 16px or 20px)
- **All components must follow monotone theme** - override ShadCN defaults if needed

---

## Development Commands

### Backend (FastAPI with uv)

```bash
# Setup
cd apps/api

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install dependencies
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"

# Database migrations
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "description"

# Run locally (Docker preferred)
docker-compose up

# Run development server (no venv activation needed)
uv run uvicorn src.main:app --reload --port 8000

# Or with activated venv:
uvicorn src.main:app --reload --port 8000

# Tests
uv run pytest tests/ -v
uv run pytest tests/integration/ -k test_sql_verification

# Lint & format
uv run ruff check src/
uv run black src/
uv run mypy src/

# Add new dependency
uv pip install <package-name>
```

### Frontend (Next.js)

```bash
# Setup
cd apps/web
pnpm install

# Run development server
pnpm dev  # runs on http://localhost:3000

# Build
pnpm build

# Type checking
pnpm typecheck

# Lint
pnpm lint

# Tests
pnpm test              # unit tests
pnpm test:e2e          # Playwright E2E tests

# Generate API client (after backend OpenAPI changes)
pnpm run codegen:api-client
```

### Full Stack

```bash
# Root directory - start all services
docker-compose up

# Stop all services
docker-compose down

# Rebuild after dependency changes
docker-compose up --build

# View logs
docker-compose logs -f api
docker-compose logs -f web
```

### OpenAPI Workflow

```bash
# 1. Backend: edit apps/api/src/openapi.json

# 2. Validate schema
python scripts/openapi.py validate

# 3. Generate TypeScript client
pnpm run codegen:api-client

# 4. Frontend now has typed client in packages/api-client/generated/
```

---

## Project Structure

```
/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── src/
│   │   │   ├── main.py         # App entry, middleware, routes
│   │   │   ├── settings.py     # Config from env vars
│   │   │   ├── models/         # SQLAlchemy models
│   │   │   ├── routes/         # API endpoints by domain
│   │   │   ├── services/       # Business logic layer
│   │   │   │   ├── bigquery.py # BQ client, query execution
│   │   │   │   ├── cache.py    # Cache adapter (Redis/in-process)
│   │   │   │   ├── compiler.py # YAML → execution plan
│   │   │   │   ├── validator.py# YAML schema validation
│   │   │   │   └── lineage.py  # Graph building
│   │   │   ├── schemas/        # Pydantic models (request/response)
│   │   │   ├── openapi.json    # OpenAPI spec (SSOT)
│   │   │   └── core/
│   │   │       ├── auth.py     # Google SSO, session mgmt
│   │   │       ├── observability.py # OpenTelemetry setup
│   │   │       └── errors.py   # Exception handlers
│   │   ├── alembic/            # Database migrations
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── web/                    # Next.js frontend
│       ├── app/                # App Router pages
│       │   ├── layout.tsx      # Root layout (app shell)
│       │   ├── page.tsx        # Home redirect
│       │   ├── login/          # Auth pages
│       │   ├── dashboards/     # Gallery
│       │   ├── dash/[slug]/    # Dashboard view
│       │   ├── edit/[slug]/    # Editor (Builder/YAML/Preview tabs)
│       │   ├── lineage/[slug]/ # Lineage graph
│       │   ├── datasets/       # Schema browser
│       │   └── settings/       # User preferences
│       ├── components/
│       │   ├── ui/             # ShadCN base components
│       │   ├── charts/         # Recharts wrappers
│       │   ├── dashboard/      # Dashboard-specific widgets
│       │   ├── layout/         # App shell components
│       │   └── editor/         # Builder, YAML editor components
│       ├── lib/
│       │   ├── api-client.ts   # TanStack Query + generated client
│       │   ├── yaml-parser.ts  # YAML ↔ UI model mapping
│       │   └── error-handling.ts
│       ├── styles/
│       │   └── globals.css     # Tailwind + custom CSS vars
│       ├── public/
│       ├── tests/
│       └── next.config.js
│
├── dashboards/                 # YAML source of truth
│   ├── revenue-dashboard.yaml
│   └── ops-kpis.yaml
│
├── packages/                   # Shared code (if monorepo)
│   └── api-client/             # Generated TypeScript client
│
├── scripts/
│   ├── openapi.py              # Validation & codegen
│   └── precompute.py           # Manual cache warming
│
├── docs/
│   ├── backend_pdr.md          # Backend design doc
│   ├── frontend_pdr.md         # Frontend design doc
│   └── ui_pdr.md               # UI/UX specifications
│
├── .claude/
│   ├── settings.json           # Hooks, agents, references
│   └── agents/
│       ├── backend-agent.md    # FastAPI specialist
│       ├── frontend-agent.md   # Next.js specialist
│       └── integration-agent.md# OpenAPI & E2E tests
│
├── docker-compose.yml          # Local dev environment
└── README.md
```

---

## Critical Implementation Details

### Backend Guardrails

**SQL Execution** (all queries):
- `maximum_bytes_billed`: 100 MB default (fail fast on expensive queries)
- `useQueryCache`: Always true (leverage BQ result cache)
- Sample limit: Return max 100 rows to LLM verification loop
- Timeout: 30s execution limit
- Service account: Read-only permissions on datasets

**Validation Flow**:
1. Parse YAML with JSON Schema
2. Extract SQL queries
3. Execute each with byte cap and timeout
4. Return metadata: schema, row count, bytes scanned, sample rows
5. Agent decides: accept or iterate

**Cache Strategy**:
- Key pattern: `dash:{slug}:q:{query_hash}:v:{version}`
- TTL: 24-48 hours (safety net, not expiration strategy)
- Precompute: Manual trigger endpoint warms cache before user access
- Compact payloads: Transform BQ results to chart-ready JSON (arrays, not verbose objects)

**Observability**:
- OpenTelemetry spans: `dashboard.compile`, `sql.run`, `data.serve`, `precompute.run`
- Trace attributes: `dashboard_slug`, `query_hash`, `bytes_scanned`, `duration_ms`, `cache_hit`
- Structured logs: JSON format with `correlation_id` from `x-correlation-id` header
- Error responses include `trace_id` for debugging

### Frontend Architecture

**Three-Panel Layout** (VS Code-inspired):
- **Left Explorer** (240px): Dashboard list, dataset tree, recent items, quick search
- **Center Workspace**: Active tabs (Dashboard View, Builder, YAML Editor, Preview)
- **Right Assistant** (320px, collapsible): LLM chat interface (stub in MVP)

**View Types** (same data, different presentation):
- **Analytical**: Multi-column grid, prominent filters, medium-large charts, default time: last 90 days
- **Operational**: Status-first, alert banners, high density, small charts, default time: today/last hour
- **Strategic**: Narrative flow, large KPIs, text blocks, minimal interactions, default time: YTD

**State Management**:
- In-memory model: Current dashboard YAML, dirty flag, last save timestamp
- Zustand or React Context for global state
- TanStack Query for server state (dashboards, data, metadata)
- No persistence beyond session (clear on navigation)

**YAML ↔ UI Binding**:
- Parser converts YAML to React component tree
- UI edits (color, type, size) update in-memory YAML model
- Renderer re-evaluates and updates instantly (no debounce)
- Save: Validate locally → POST to backend → Reset dirty flag

**Freshness Indicators**:
- Global: Header shows "As of Oct 30, 10:15 AM"
- Per-card: Footer shows "Source: revenue_daily_mv (p2025-10-30)"
- Color coding: Green (<1h), Yellow (1-4h), Red (>4h), Grey (unknown)

### Authentication & Security

**Google SSO**:
- OAuth 2.0 flow: Frontend redirects to Google → Backend validates token → Check email allowlist
- Allowlist: Comma-separated emails in env var `ALLOWED_EMAILS` or Secret Manager
- Session: HTTP-only cookie, 7-day expiration, stored in Postgres
- Middleware: Protect all `/api/*` routes except `/auth/*` and `/health`

**Authorization (MVP)**:
- Coarse-grained: All authenticated users have full access
- Owner field in dashboards is tracking only, not enforced
- Future: Row-level security (RLS) and role-based access

**Secrets**:
- Secret Manager: BigQuery service account, OAuth client ID/secret, DB credentials
- Never expose: Service account keys, session secrets, API tokens
- Frontend: No secrets in code or .env.local (only public vars like `NEXT_PUBLIC_API_URL`)

### Error Handling

**Backend Error Format** (standard response):
```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",           // Machine-readable code
    "message": "Daily BigQuery budget exceeded", // Human-readable
    "details": { "bytes_scanned": 1000000000 }, // Additional context
    "trace_id": "abc123",               // Correlation ID
    "remediation": "Try reducing query complexity or wait until tomorrow"
  }
}
```

**Frontend Error Classification**:
- `network`: Connection failed, retry automatically
- `auth`: 401, redirect to login
- `validation`: 422, show inline errors
- `quota`: 429, show budget warning banner
- `server`: 5xx, retry with exponential backoff
- `client`: Other 4xx, show error message with trace ID

**Error Boundaries**:
- App-level: Catches all React errors, shows fallback UI
- Route-level: Per-page error boundaries
- Component-level: Chart/table error states (inline, don't crash page)

---

## Dashboard YAML Schema

**Example Structure**:
```yaml
version: 0
kind: dashboard
slug: revenue-dashboard
title: "Revenue Dashboard"
owner: sarah@company.com
view_type: analytical  # analytical | operational | strategic

layout:
  - id: rev_kpi
    type: kpi
    query_ref: q_revenue_total
    style:
      size: small      # small | medium | large | xlarge
      position: { row: 0, col: 0, width: 3, height: 1 }

  - id: rev_trend
    type: chart
    chart: line        # line | bar | area | table
    query_ref: q_revenue_daily
    config:
      x_axis: date
      y_axis: revenue
      series: region
    style:
      color: neutral   # In monotone theme: neutral (grey), success, warning, error
      size: medium
      position: { row: 1, col: 0, width: 6, height: 2 }

queries:
  - id: q_revenue_total
    warehouse: bigquery
    sql: |
      SELECT SUM(revenue) AS total_revenue
      FROM mart.revenue_daily
      WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)

  - id: q_revenue_daily
    warehouse: bigquery
    sql: |
      SELECT date, region, SUM(revenue) AS revenue
      FROM mart.revenue_daily
      WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
      GROUP BY date, region
      ORDER BY date
```

**Validation Rules**:
- Required fields: `version`, `kind`, `slug`, `title`, `layout`, `queries`
- `slug`: Lowercase, hyphenated, unique
- Each `layout` item must reference valid `query_ref`
- SQL must be valid BigQuery syntax
- Position coordinates: 12-column grid (width: 1-12)

---

## Common Development Workflows

### Adding a New Dashboard Manually

1. Create YAML file in `/dashboards/my-dashboard.yaml`
2. Validate: `curl -X POST http://localhost:8000/api/dashboards/validate -d @dashboards/my-dashboard.yaml`
3. Save: `curl -X POST http://localhost:8000/api/dashboards/save -d @dashboards/my-dashboard.yaml`
4. Access in frontend: `http://localhost:3000/dash/my-dashboard`

### Running Precompute for Faster Loads

```bash
# Warm cache for a specific dashboard
curl -X POST http://localhost:8000/api/precompute \
  -H "Content-Type: application/json" \
  -d '{"slug": "revenue-dashboard"}'

# Verify cache hit (should return <300ms on repeat)
curl http://localhost:8000/api/data/revenue-dashboard
```

### Adding a New Chart Type

**Backend** (apps/api/src/services/compiler.py):
1. Add chart type to validation schema
2. Implement data transformation for new type
3. Update response format

**Frontend** (apps/web/components/charts/):
1. Create new component: `HeatmapChart.tsx` (or similar)
2. Use Recharts or custom rendering (maintain monotone theme)
3. Add to chart factory in `ChartRenderer.tsx`
4. Update YAML mapper to recognize new type

### Debugging LLM Verification Loop

1. Check backend logs for `sql.run` spans
2. Look for `bytes_scanned`, `row_count`, `sample_rows` in trace
3. If agent rejects: Check validation logic in agent prompt
4. If query fails: Check BigQuery error in `details` field
5. Manual test: Hit `/api/sql/run` with sample SQL

### Handling Cache Misses

**Symptoms**: Dashboard loads slowly, backend logs show BigQuery execution

**Diagnosis**:
1. Check cache key in logs: `cache.get(dash:{slug}:q:{hash}:v:{version})`
2. Verify cache hit/miss in trace attributes
3. Check Redis connection (if using Redis): `redis-cli ping`

**Resolution**:
1. Manual precompute: `POST /api/precompute`
2. If cache cold: First user triggers execution, subsequent users hit cache
3. If version changed: Cache invalidates automatically (expected)

---

## Testing Strategy

### Backend Tests

**Unit Tests** (pytest):
- `tests/unit/test_validator.py`: YAML schema validation
- `tests/unit/test_compiler.py`: YAML → execution plan conversion
- `tests/unit/test_cache.py`: Cache key generation, TTL behavior

**Integration Tests** (pytest with fixtures):
- `tests/integration/test_sql_run.py`: Mock BigQuery client, verify sample limiting
- `tests/integration/test_precompute.py`: End-to-end cache population
- `tests/integration/test_lineage.py`: Graph generation from YAML

**Run Specific Tests**:
```bash
pytest tests/unit/test_validator.py -v
pytest tests/integration/ -k test_sql_verification
pytest tests/ --cov=src --cov-report=html
```

### Frontend Tests

**Component Tests** (React Testing Library):
- `tests/components/charts/LineChart.test.tsx`: Chart rendering with mock data
- `tests/components/dashboard/KpiTile.test.tsx`: Delta calculation, color coding

**E2E Tests** (Playwright):
- `tests/e2e/auth.spec.ts`: Google SSO flow (stub for local)
- `tests/e2e/dashboard-view.spec.ts`: Load dashboard, verify charts render
- `tests/e2e/editor.spec.ts`: Change color in Builder → Save → Reload → Verify persistence
- `tests/e2e/lineage.spec.ts`: Open lineage view, click nodes, verify metadata

**Run E2E Tests**:
```bash
cd apps/web
pnpm test:e2e                    # All E2E tests
pnpm test:e2e --headed           # With browser visible
pnpm test:e2e --debug            # Step-through debugging
pnpm test:e2e tests/e2e/editor.spec.ts  # Single test file
```

### Contract Tests

**OpenAPI Validation**:
```bash
# Validate schema is valid OpenAPI 3.0
python scripts/openapi.py validate

# Test backend responses match schema
pytest tests/contract/test_openapi_compliance.py
```

---

## Environment Variables

### Backend (.env for apps/api/)

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/peter_db

# BigQuery
GOOGLE_CLOUD_PROJECT=my-gcp-project
BIGQUERY_DATASET=analytics
BIGQUERY_CREDENTIALS_PATH=/path/to/service-account.json  # Or use Secret Manager
BIGQUERY_MAX_BYTES_BILLED=100000000  # 100 MB default

# Cache
CACHE_TYPE=redis  # redis | in-process
REDIS_URL=redis://localhost:6379/0

# Auth
GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=xxx  # From Secret Manager
ALLOWED_EMAILS=sarah@company.com,mike@company.com  # Comma-separated

# Session
SESSION_SECRET=xxx  # From Secret Manager
SESSION_COOKIE_SECURE=true  # Set false for local dev

# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318  # Optional
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR

# App
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,https://app.example.com
```

### Frontend (.env.local for apps/web/)

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Auth (redirects)
NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Feature flags (optional)
NEXT_PUBLIC_ENABLE_ASSISTANT=false  # LLM chat stub in MVP
```

---

## Proactive Agent Usage

The `.claude/agents/` directory contains specialized agents that should be invoked automatically based on task keywords:

### Backend Agent
**Triggers**: "create endpoint", "add model", "setup cache", "implement LLM streaming", "add migration", "optimize query"

**Responsibilities**:
- FastAPI route implementation
- SQLAlchemy models and Alembic migrations
- BigQuery query execution with guardrails
- Redis/cache configuration
- OpenTelemetry instrumentation

### Frontend Agent
**Triggers**: "create component", "build page", "implement UI", "add form", "style with Tailwind", "implement SSE streaming"

**Responsibilities**:
- Next.js pages and layouts
- ShadCN component integration (strict monotone theme)
- Recharts chart wrappers
- State management (Zustand/Context)
- Two-way YAML ↔ UI binding
- Responsive design (mobile, tablet, desktop)

### Integration Agent
**Triggers**: "generate API client", "validate schema", "setup error handling", "add tracing", "write E2E test"

**Responsibilities**:
- OpenAPI schema validation and TypeScript client generation
- Error standardization (backend format, frontend classification)
- Correlation IDs (x-correlation-id header flow)
- E2E tests (Playwright)
- Contract tests (OpenAPI compliance)

**Important**: When user requests match these triggers, proactively suggest using the relevant agent to ensure consistency with the PDRs.

---

## Performance Budgets

### Backend
- Dashboard data serving (warm cache): p95 < 300ms
- Dashboard data serving (cold cache): p95 < 1.5s
- SQL verification endpoint: p95 < 2s (for <1 GB scans)
- Precompute operation: p95 < 5s per dashboard

### Frontend
- Dashboard view (cached): p95 < 500ms load
- Dashboard view (cold): p95 < 2s load
- Individual chart render: p95 < 200ms
- Editor Time to Interactive: p95 < 3s
- Main bundle: < 200 KB gzipped
- Dashboard view bundle: < 150 KB additional
- Lighthouse performance score: > 90
- Lighthouse accessibility score: > 95

### Network
- Dashboard payload: < 300 KB compressed
- Individual chart payload: < 100 KB
- Single API call per dashboard (no waterfall)

---

## Accessibility Requirements

- **Keyboard navigation**: All interactive elements reachable via Tab, Enter activates, Escape closes
- **Focus indicators**: 2px solid ring, high contrast (black in light mode, white in dark mode)
- **Screen readers**: ARIA labels on charts (`role="img"`, descriptive `aria-label`), semantic HTML, proper heading hierarchy
- **Color contrast**: WCAG AA compliance (4.5:1 for normal text, 3:1 for large text)
- **Charts**: Text alternatives available, keyboard navigation through data points, patterns not just color for series
- **Zoom**: Usable up to 200% browser zoom without loss of functionality
- **Motion**: Respect `prefers-reduced-motion` (disable animations when set)

---

## Common Gotchas & Tips

### YAML Editing
- **Indentation matters**: Use 2 spaces (not tabs)
- **Query refs must exist**: Every `layout` item's `query_ref` must match a query `id`
- **Grid coordinates**: 12-column system, width: 1-12, positions must not overlap
- **Color in monotone theme**: Use `neutral` (grey) as default, semantic colors sparingly

### BigQuery Queries
- **Always use `DATE_SUB(CURRENT_DATE(), INTERVAL n DAY)`** for date filters (not hardcoded dates)
- **Include `maximum_bytes_billed`** in all execution contexts
- **Partition filters**: Reference partition columns in WHERE for performance
- **Clustering**: Consider clustering columns for common GROUP BY patterns

### Caching
- **Version changes invalidate**: Changing YAML bumps version, cache misses expected
- **Precompute before peak hours**: Warm cache manually to ensure fast first load
- **TTL is safety net**: Don't rely on TTL for freshness; use explicit precompute

### Frontend State
- **No autosave**: Dirty state persists until explicit Save
- **Confirmation on navigate**: Prevent accidental loss with dirty state
- **In-memory only**: State clears on tab close (no localStorage in MVP)

### Monotone Theme Compliance
- **Avoid branded colors in UI**: No blue buttons, no green success checkmarks in chrome
- **Use black/white/grey hierarchy**: Rely on typography weight, size, and spacing for hierarchy
- **Semantic colors for data only**: Charts can use color when it conveys meaning (e.g., positive/negative)
- **Test in both light and dark modes**: Ensure contrast meets standards in both themes

---

## MVP Acceptance Criteria

### Must Have (Week 8)
- [ ] Google SSO authentication functional
- [ ] Dashboard gallery displays all dashboards, search works
- [ ] Dashboard view renders all three view types (Analytical, Operational, Strategic)
- [ ] Charts render with Recharts (line, bar, area, table supported)
- [ ] Freshness indicators visible per card and globally
- [ ] Editor: Builder tab allows visual edits (color, type, size)
- [ ] Editor: YAML tab allows direct text editing with validation
- [ ] Editor: Preview tab shows live rendering
- [ ] Save workflow: dirty state tracking, validation, persistence
- [ ] Lineage view: graph displays dashboard → charts → queries → tables
- [ ] Two reference dashboards created via LLM chat
- [ ] SQL verification loop: agent proposes → backend executes → metadata returned
- [ ] Precompute: manual trigger warms cache, subsequent loads <300ms
- [ ] Backend: all API endpoints functional (validate, compile, save, sql/run, precompute, data, lineage)
- [ ] Observability: OpenTelemetry spans for critical paths, correlation IDs flow end-to-end

### Performance
- [ ] Dashboard cached load: p95 < 500ms
- [ ] Dashboard cold load: p95 < 2s
- [ ] Chart render: p95 < 200ms
- [ ] Main bundle: < 200 KB gzipped

### Accessibility
- [ ] Keyboard navigation: all elements reachable via Tab
- [ ] Focus indicators: 2px ring visible
- [ ] Screen reader: charts have descriptive ARIA labels
- [ ] Color contrast: WCAG AA (4.5:1)
- [ ] Zoom: 200% maintains usability

### Responsive
- [ ] Mobile (<640px): single column, readable
- [ ] Tablet (640-1024px): 2-3 columns, functional
- [ ] Desktop (>1024px): full layout with persistent rails

---

## Phase Roadmap Preview

### Phase 1 (Weeks 9-12)
- Pub/Sub-driven "New data available" banner
- Table virtualization for long lists
- Chart annotation library (ReferenceLine/Area)
- Saved filter presets
- Role-based view toggles (viewer/editor)
- Memorystore upgrade for multi-instance cache consistency

### Phase 2/3 (Months 4-6)
- Custom widget types (heatmaps, Sankey, network graphs)
- Dashboard templating with variables/parameters
- Slack/Linear context panel for LLM
- Multi-user collaboration (presence, optimistic locking)
- Public share links and embedded dashboards
- PDF/PowerPoint export

---

## Support & References

- **Backend PDR**: `docs/backend_pdr.md` (authoritative backend design)
- **Frontend PDR**: `docs/frontend_pdr.md` (authoritative frontend design)
- **UI PDR**: `docs/ui_pdr.md` (visual specs, component inventory, interaction patterns)
- **OpenAPI Schema**: `apps/api/src/openapi.json` (single source of truth for API contract)
- **Agent Configs**: `.claude/agents/` (proactive agent instructions)

---

## Contributing Guidelines

1. **Follow the monotone theme strictly**: No deviations from black/white/grey palette in UI chrome
2. **PDRs are authoritative**: When in doubt, refer to PDRs; they define acceptance criteria
3. **OpenAPI first**: Update schema before implementing endpoints; generate client before frontend work
4. **Test coverage**: Unit tests for business logic, E2E tests for user journeys
5. **Performance budgets**: CI blocks deployment if budgets exceeded
6. **Accessibility**: Test with keyboard, screen reader, and color contrast tools before PR
7. **Observability**: Add spans for new critical paths, include correlation IDs in errors
8. **No premature optimization**: Implement features per PDR, measure, then optimize if needed

---

## Quick Start for New Developers

1. **Read PDRs**: Spend 30 minutes reading backend, frontend, and UI PDRs
2. **Setup environment**: Run `docker-compose up` to start all services
3. **Verify setup**:
   - Backend health: `curl http://localhost:8000/health`
   - Frontend: Open `http://localhost:3000` in browser
4. **Create sample dashboard**: Use LLM chat or import YAML from `/dashboards/`
5. **Explore codebase**: Start with `apps/api/src/main.py` and `apps/web/app/layout.tsx`
6. **Run tests**: `pytest` in backend, `pnpm test` in frontend to ensure setup correct
7. **Make first change**: Try editing a dashboard in Builder, save, verify YAML updated

---

**Last Updated**: 2025-10-30
**Project Status**: Week 1 - Foundation & Setup
**Next Milestone**: MVP Completion (Week 8)
- Never use paceholder data
- Never limit data unless specified in the prompt
- Never craete doc files unless requested- provide summary within the chat