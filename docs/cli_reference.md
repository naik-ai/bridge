# Peter Dashboard CLI Operations Reference

Single source for backend and frontend command-line workflows in the Peter Dashboard project. Use it as a quick refresher or a deeper guide when you need the “why” behind a command.

---

## 1. Quick Start Cheat Sheet

### Backend Essentials
- `make setup` – bootstrap API environment (dependencies, migrations, sample data)
- `make dev` – run API + backing services locally with fast reload
- `make up` / `make down` – start/stop full Docker stack (API, Postgres, Redis, web)
- `make db-migrate` / `make db-migrate-create MSG="..."` – apply or create migrations
- `make dash-validate FILE=...` – validate dashboard YAML (schema + SQL dry run)
- `make dash-precompute SLUG=...` – warm cache for a dashboard

### Frontend Essentials
- `make web-install` – install Next.js + workspace dependencies (pnpm)
- `make web-dev` – start frontend dev server on http://localhost:3000
- `make web-codegen` – regenerate TypeScript client from OpenAPI spec
- `make web-lint`, `make web-typecheck`, `make web-test` – quality gates before commit
- `make web-build` / `make web-start` – production build & serve

### Full-Stack Workflow
- `make dev-full` – start API (8000) + Web (3000) together
- `make ci-web`, `make ci-all` – frontend-only or end-to-end CI checks
- `make api-health`, `make api-routes` – smoke test backend while iterating on web

---

## 2. Backend CLI Guide

### 2.1 Environment Setup
```bash
make setup          # Installs Python deps (uv), formats env, runs migrations
make dev            # Starts API with autoreload + Dockerised Postgres/Redis
```
Use `make up` when you need the full Docker stack (mirrors production) and `make logs-api` to tail API output.

### 2.2 Database Operations
```bash
make db-migrate             # Apply pending migrations
make db-migrate-create MSG="add lineage tables"
make db-rollback            # Revert last migration
make db-reset               # Drop + recreate (destructive)
make db-shell               # psql with project credentials
make db-seed                # Load sample users/dashboards
```
> Tip: run `make db-seed` after `make setup` to populate dashboards (`revenue-dashboard`, `ops-kpis`) and YAML fixtures in `dashboards/`.

### 2.3 Dashboard & YAML Management
```bash
make dash-list
make dash-validate FILE=dashboards/revenue-dashboard.yaml
make dash-precompute SLUG=revenue-dashboard
make dash-delete SLUG=stale-dashboard
```
Validation checks YAML schema, query references, layout overlaps, and executes a BigQuery dry run for SQL syntax.

### 2.4 Caching & Observability
```bash
make cache-stats
make cache-flush
make api-health
make api-routes
```
Used during verification loop debugging and to confirm precompute warms the cache (`dash:{slug}:...` keys).

### 2.5 Quality & Testing
```bash
make test           # Backend unit/integration suite
make test-cov       # Include coverage details
make lint           # Ruff + mypy (configured in pyproject)
make format         # Apply Black + isort formatting
```

### 2.6 Release Checkpoints
1. `make lint && make test-cov`
2. `make db-migrate` (confirm migrations apply cleanly)
3. `make dash-precompute SLUG=<critical dashboards>`
4. `make api-health`
5. Commit with meaningful message, then run `make ci-all` before pushing.

---

## 3. Frontend CLI Guide

### 3.1 Setup & Daily Start
```bash
make web-install           # pnpm install in apps/web + packages
make web-codegen           # Sync generated TypeScript client to backend spec
make web-dev               # Next.js dev server with Fast Refresh
```
Ensure `apps/web/.env.local` contains:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=...apps.googleusercontent.com
NEXT_PUBLIC_ENABLE_ASSISTANT=false
```

### 3.2 Build & Serve
```bash
make web-build             # Production build (.next output)
make web-start             # Serve production bundle locally
make web-clean             # Remove .next/out caches for a fresh build
```

### 3.3 Code Quality & Testing
```bash
make web-lint              # ESLint (Next.js + custom rules)
make web-typecheck         # tsc against generated types
make web-test              # Vitest unit tests
make web-test-e2e          # Playwright flows (auth, dashboards, editor)
make ci-web                # Combined lint + typecheck + build
```

### 3.4 API Client Generation
```bash
make web-codegen
```
Generates `packages/api-client/generated/**/*` via `openapi-typescript-codegen`. Always rerun after backend OpenAPI updates to keep types consistent.

### 3.5 Common Workflows
- **Morning routine**: `git pull && make web-install && make web-codegen && make web-dev`
- **Before commit**: `make web-lint && make web-typecheck && make web-test`
- **Before push**: `make ci-web`
- **When API schema changes**: regenerate client, fix TypeScript errors surfaced in Next.js console/IDE.

### 3.6 Troubleshooting
| Issue | Fix |
|-------|-----|
| Port 3000 busy | `lsof -ti:3000 \| xargs kill -9` |
| Type errors after backend change | `make web-codegen && make web-typecheck` |
| Stale build artefacts | `make web-clean && make web-dev` |
| API unreachable | `make api-health` (backend) then check `NEXT_PUBLIC_API_URL` |

---

## 4. Full-Stack Utilities & Shared Workflows

- `make setup-full` – install + provision both backend and frontend prerequisites
- `make dev-full` – launches API + Next.js for end-to-end testing
- `make logs` / `make logs-api` / `make logs-web` – follow container logs when running under Docker
- `make ps` – view status of all docker-compose services
- `make clean` / `make teardown` – stop containers and remove volumes/images (useful before switching branches)

### Smoke Testing a Feature End-to-End
1. Start backend: `make dev`
2. Start frontend: `make web-dev` (or `make dev-full`)
3. Create or edit dashboard YAML, then `make dash-validate`
4. Hit `http://localhost:3000/dash/<slug>` and verify charts; check freshness + bytes scanned badges
5. Run `make web-test-e2e` if the change affects onboarding or critical flows

### When to Prefer Docker (`make up`)
- Verifying Cloud Run parity (Gunicorn + Uvicorn workers)
- Ensuring Postgres/Redis versions align with production
- Running integration tests that rely on container networking

---

## 5. Reference Tables

### Backend Command Index
| Command | Purpose |
|---------|---------|
| `make help` | Show all targets |
| `make dev` | Fast local API dev |
| `make up` | Full dockerised stack |
| `make db-migrate` / `db-rollback` | Apply/undo migrations |
| `make db-seed` | Load sample data |
| `make dash-validate` | Validate YAML & SQL |
| `make dash-precompute` | Warm cache |
| `make cache-flush` | Clear Redis/in-memory cache |
| `make api-shell` | Python REPL with app context |
| `make test`, `make lint` | Quality gates |

### Frontend Command Index
| Command | Purpose |
|---------|---------|
| `make web-install` | Install dependencies (pnpm) |
| `make web-dev` | Next.js dev server |
| `make web-build` / `web-start` | Production assets & serve |
| `make web-clean` | Clear Next.js cache |
| `make web-codegen` | Regenerate API client |
| `make web-lint`, `web-typecheck` | Quality gates |
| `make web-test`, `web-test-e2e` | Unit & E2E tests |
| `make ci-web` | Frontend CI workflow |
| `make dev-full` | Run API + Web together |

---

## 6. Tips & Best Practices
- **Prefer `make dev` + `make web-dev` during feature work** for fast reload loops; switch to `make up` before handoff or release reviews.
- **Regenerate the API client early** after backend changes to surface TypeScript regressions before merging.
- **Use validation + precompute before demos** to ensure cache hits and accurate freshness indicators.
- **Commit with context**: mention relevant dashboards or services (`feat: dashboard-editor autosave`) to align with task tracking in `docs/task.md`.
- **Document new commands here** whenever Makefile targets are added or renamed so onboarding stays painless.

---

**Last Updated:** 2025-10-30  
**Maintainers:** Platform Engineering (backend + frontend leads)
