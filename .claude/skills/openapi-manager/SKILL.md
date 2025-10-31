# OpenAPI Manager Skill

**Purpose**: Manage the OpenAPI schema as the Single Source of Truth (SSOT) for API contracts, generate TypeScript clients, and prevent breaking changes.

## When to Use This Skill

Use this skill when:
- Backend updates API endpoints or models
- Frontend needs type-safe API client
- Validating OpenAPI schema before commit
- Checking for breaking changes in PRs
- Ensuring frontend/backend contract alignment

## Critical Commands for MVP

### 1. Validate Schema

```bash
# Run from project root
python scripts/openapi.py validate
```

**What it does**:
- Validates `apps/api/src/openapi.json` against OpenAPI 3.1 spec
- Checks for missing required fields, invalid types, broken refs
- Blocks commit if validation fails (pre-commit hook)

**When to use**: Before every commit touching backend API

### 2. Generate TypeScript Client

```bash
# Run from project root
pnpm run codegen:api-client
# Or directly:
python scripts/openapi.py generate
```

**What it does**:
- Reads `apps/api/src/openapi.json`
- Generates TypeScript client in `packages/api-client/generated/`
- Creates:
  - `types.ts` - Type definitions (TripCreate, TripResponse, etc.)
  - `api.ts` - API client functions (getTrips, createTrip, etc.)
  - `index.ts` - Exports

**When to use**:
- After backend updates OpenAPI schema
- During Week 1 setup (initial codegen)
- In CI/CD pipeline after API changes

### 3. Check Breaking Changes

```bash
python scripts/openapi.py check-breaking --base=main
```

**What it does**:
- Compares current OpenAPI schema with `main` branch
- Detects breaking changes:
  - Removed endpoints
  - Removed required fields
  - Changed response types
  - Stricter validation rules
- Exits with error code if breaking changes found

**When to use**:
- In PR CI checks
- Before merging backend changes
- During Week 2-3 when iterating on API

## Integration with Agents

### Backend Agent Workflow

When backend-agent modifies API:

```python
# 1. Update FastAPI endpoint
@app.post("/api/v1/trips", response_model=TripResponse)
async def create_trip(trip: TripCreate):
    # Implementation...
    pass

# 2. Update OpenAPI schema
# Edit apps/api/src/openapi.json manually OR
# Use FastAPI's built-in schema generation:
python scripts/openapi.py extract-from-fastapi  # Extracts from app
```

```bash
# 3. Validate schema
python scripts/openapi.py validate

# 4. Generate client (triggers frontend update)
pnpm run codegen:api-client

# 5. Commit both schema + generated client
git add apps/api/src/openapi.json packages/api-client/generated/
git commit -m "Add trip creation endpoint"
```

### Frontend Agent Workflow

When frontend-agent needs to call API:

```typescript
// ✅ CORRECT: Use generated client
import { tripsApi } from '@/api-client'

const trips = await tripsApi.getTrips()  // Fully typed!
// trips: TripResponse[]

// ❌ WRONG: Manual fetch
const res = await fetch('/api/trips')
const trips: any = await res.json()  // NO!
```

### Integration Agent Workflow

When integration-agent runs tests:

```bash
# 1. Ensure schema is valid
python scripts/openapi.py validate

# 2. Run contract tests (schema vs actual backend)
pytest tests/contract/test_openapi_compliance.py

# 3. Run E2E tests with generated client
pnpm run test:e2e
```

## MVP Workflow Examples

### Week 1: Initial Setup

```bash
# Backend creates OpenAPI schema
cd apps/api
# Create src/openapi.json with basic endpoints

# Validate schema
python scripts/openapi.py validate

# Generate client (first time)
cd ../..
pnpm run codegen:api-client

# Frontend uses generated client
cd apps/web
# Import and use @/api-client in components
```

### Week 2: Adding LLM Streaming Endpoint

```bash
# 1. Backend adds /ai/plan endpoint to openapi.json
# apps/api/src/openapi.json:
# paths:
#   /api/v1/ai/plan:
#     post:
#       operationId: streamPlan
#       requestBody:
#         required: true
#         content:
#           application/json:
#             schema:
#               type: object
#               properties:
#                 trip_id: {type: string, format: uuid}
#                 prompt: {type: string}

# 2. Validate
python scripts/openapi.py validate

# 3. Regenerate client
pnpm run codegen:api-client

# 4. Frontend uses new endpoint
# import { aiApi } from '@/api-client'
# const stream = await aiApi.streamPlan({ trip_id, prompt })
```

### Week 3: Preventing Breaking Changes

```bash
# Before merging PR that changes API:

# 1. Check for breaking changes
python scripts/openapi.py check-breaking --base=main

# Output example:
# ❌ BREAKING: Removed endpoint GET /api/v1/trips
# ❌ BREAKING: Field 'name' changed from optional to required in TripUpdate
# ✅ NON-BREAKING: Added new endpoint POST /api/v1/trips/archive

# 2. If breaking changes found:
#    - Document migration path
#    - Coordinate with frontend team
#    - Version API if needed (e.g., /api/v2/...)

# 3. If safe, regenerate client and test
pnpm run codegen:api-client
pnpm run test:e2e
```

## Pre-Commit Hook Integration

This skill is automatically triggered by the pre-commit hook:

```json
// .claude/settings.json
{
  "hooks": {
    "pre-commit": "python scripts/openapi.py validate && pnpm run codegen:api-client"
  }
}
```

**What happens on commit**:
1. Schema validation runs automatically
2. If validation fails → commit blocked
3. If schema changed → client regenerated automatically
4. Ensures frontend/backend always in sync

## File Ownership

This skill manages:

```
/
├── apps/api/src/openapi.json       # SSOT - OpenAPI schema
├── packages/api-client/            # Generated TypeScript client
│   └── generated/
│       ├── index.ts
│       ├── api.ts
│       └── types.ts
└── scripts/openapi.py              # Validation + codegen logic
```

## Error Handling

Common errors and fixes:

### Error: "Invalid reference $ref"
```bash
# Problem: Broken schema reference
# Fix: Check that all $ref paths exist in openapi.json
# Example:
# components:
#   schemas:
#     TripResponse:  # Must exist!
```

### Error: "Required field missing"
```bash
# Problem: Schema missing required OpenAPI fields
# Fix: Ensure all paths have:
#   - operationId (unique identifier)
#   - responses (at least 200)
#   - tags (for grouping)
```

### Error: "Breaking change detected"
```bash
# Problem: Changed API contract without versioning
# Fix: Either:
#   1. Revert the change (if unintentional)
#   2. Create /api/v2/ endpoint (if intentional breaking change)
#   3. Make change non-breaking (add optional field instead of required)
```

## Testing Checklist

- [ ] OpenAPI schema validates (`python scripts/openapi.py validate`)
- [ ] TypeScript client generates without errors (`pnpm run codegen:api-client`)
- [ ] No breaking changes vs main (`python scripts/openapi.py check-breaking`)
- [ ] Contract tests pass (schema matches backend responses)
- [ ] E2E tests use generated client (no manual fetch calls)
- [ ] Pre-commit hook blocks invalid schemas

## References

- **OpenAPI Spec**: https://spec.openapis.org/oas/v3.1.0
- **Backend PDR**: `docs-pdr/backend_pdr.md` (§12 - OpenAPI as SSOT)
- **Frontend PDR**: `docs-pdr/frontend_pdr.md` (generated client usage)
- **Integration PDR**: `docs-pdr/project_agents.md` (contract testing)

## Activation Triggers

Use this skill when you see:
- "update OpenAPI schema"
- "generate API client"
- "validate schema"
- "check breaking changes"
- "frontend/backend out of sync"
- "type errors in API calls"
