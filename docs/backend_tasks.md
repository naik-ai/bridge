# Backend Implementation Tasks

**Project**: Bridge (Peter Dashboard Platform)
**Last Updated**: 2025-11-12
**Status**: Foundation complete, onboarding and chat features pending

---

## Completion Summary

- **Phase 1**: ✅ Complete (Foundation & Setup)
- **Phase 2**: ✅ Complete (Core Services except Phase 2.12)
- **Phase 2.12**: 📝 Documented, not implemented (Universal AI SDK)
- **Phase 3**: ✅ Complete (API Endpoints)
- **Phase 0**: ✅ Complete (Minimal Team Onboarding - Enhanced with multi-DB support)
- **Phase 3.5**: ⏳ Pending (Dashboard Generation via LLM)
- **Phase 4**: ⏳ Pending (Dashboard Data Serving)

---

## Phase 1: Foundation & Setup ✅ COMPLETE

**Duration**: Completed 2025-10-30
**PDR Reference**: Backend PDR §1

### 1.1 Project Structure
- [x] Initialize FastAPI project with uv
- [x] Create src/ directory structure
- [x] Add pyproject.toml with dependencies
- [x] Configure Docker and docker-compose.yml
- [x] Add .env.example with all required variables

### 1.2 Database Setup
- [x] Configure SQLModel with PostgreSQL
- [x] Setup Alembic for migrations
- [x] Create initial migration
- [x] Add database session management

### 1.3 Core Configuration
- [x] Create settings.py with environment variables
- [x] Setup logging configuration
- [x] Add health check endpoint
- [x] Configure CORS middleware

---

## Phase 2: Core Services & Business Logic ✅ COMPLETE (Except 2.12)

**Duration**: Completed 2025-10-30
**PDR Reference**: Backend PDR §2

### 2.1-2.11 Core Services
- [x] Implemented all MVP business logic services
- [x] Database models and relationships
- [x] Service layer pattern established
- [x] Validation and error handling

### 2.12 Universal AI SDK Infrastructure ⏳ PENDING

**Duration**: ~7 hours | **Priority**: CRITICAL - MVP BLOCKER
**PDR Reference**: Backend PDR §2.12

**Status**: Documented but not yet implemented. Required for Phase 3.5 (Dashboard Generation).

#### 2.12.1 Core Abstractions (1.5 hours)
- [ ] Create `src/ai_sdk/core/provider.py` with ProviderAdapter abstract base class
- [ ] Define methods: stream_completion(), supports_prompt_caching(), supports_tool_use()
- [ ] Create `src/ai_sdk/core/session.py` with SessionState class
- [ ] Fields: session_id, messages[], prompt_blocks[], tool_results[], state (active/completed/failed)

#### 2.12.2 Provider Adapters (2 hours)
- [ ] Create `src/ai_sdk/providers/anthropic_adapter.py`
  - Implement Anthropic Messages API streaming
  - Add prompt caching support (cache_control: ephemeral)
  - Tool use with tool_choice controls
- [ ] Create `src/ai_sdk/providers/openai_adapter.py`
  - Implement OpenAI Chat Completions streaming
  - Function calling support
- [ ] Add provider factory in `src/ai_sdk/core/provider_factory.py`

#### 2.12.3 Session Management (1.5 hours)
- [ ] Create SessionManifest model (SQLModel)
  - Fields: id, user_id, provider_name, total_tokens, created_at, ended_at, gcs_log_path
- [ ] Implement SessionManager in `src/ai_sdk/core/session_manager.py`
  - create_session(), end_session(), get_session()
  - append_message(), load_history()
- [ ] Add GCS logging for session transcripts

#### 2.12.4 Prompt Block System (1 hour)
- [ ] Create PromptBlock model (SQLModel)
  - Fields: id, name, content, cache_control (ephemeral/none), version, active
- [ ] Create PromptBlockService
  - get_active_blocks(), create_block(), update_block()
  - Inject blocks at message index 0 for all sessions

#### 2.12.5 Tool Registry (1 hour)
- [ ] Create `src/ai_sdk/tools/base.py` with ToolDefinition abstract class
- [ ] Define execute() method signature: async execute(**kwargs) -> dict
- [ ] Create ToolRegistry in `src/ai_sdk/core/tool_registry.py`
  - register_tool(), get_tool(), list_tools()
  - JSON Schema generation for tool parameters

---

## Phase 0: Minimal Team Onboarding ✅ COMPLETE

**Duration**: Completed 2025-11-12 (4 hours actual)
**PDR Reference**: Backend PDR §0 (Enhanced from task_reorganization_plan.md)

**Philosophy**: Minimal models (4 tables), defer heavy onboarding to Phase X post-MVP.

**Note**: Implemented with multi-database support (BigQuery, Postgres, Snowflake) beyond original BigQuery-only scope. Also included basic schema storage in JSONB for Table model (column metadata deferred to Phase X).

### 0.1 Database Models & Migrations ✅

#### 0.1.1 Team Model ✅
- [x] Create Team model (SQLModel) in `src/models/db_models.py`
  - Fields: id (UUID), name, slug, created_at, updated_at
  - Indexes: unique on slug
  - Note: Deferred admin_user_id to Phase X (multi-user teams)

#### 0.1.2 Connection Model ✅
- [x] Create Connection model (SQLModel)
  - Fields: id, team_id (FK), name, connection_type (enum: bigquery/postgres/snowflake), credentials_path (GCS), status (testing/active/failed), last_tested_at, created_at, updated_at
  - Indexes: team_id, status
  - Enhanced: Multi-database support vs BigQuery-only in original spec

#### 0.1.3 Dataset Model ✅
- [x] Create Dataset model (SQLModel)
  - Fields: id, connection_id (FK), name, fully_qualified_name, description, catalog_job_id, catalog_job_status, discovered_at, last_scanned_at
  - Indexes: connection_id, fully_qualified_name (unique per connection)

#### 0.1.4 Table Model ✅
- [x] Create Table model (SQLModel)
  - Fields: id, dataset_id (FK), name, fully_qualified_name, description, schema (JSONB), row_count, size_bytes, discovered_at, last_scanned_at
  - Indexes: dataset_id, fully_qualified_name (unique per dataset)
  - Enhanced: Added schema JSONB field for column metadata (basic support, full Column model deferred to Phase X)

#### 0.1.5 Migrations ✅
- [x] Create Alembic migration: `1ace71fc4600_add_onboarding_tables.py`
- [x] Migration includes all 4 tables with proper indexes and constraints

**Deferred Models** (to Phase X post-MVP):
- Column, PIIDetection, DbtArtifact, DocSource, GlossaryTerm, BusinessGoal, DataPolicy, OnboardingReport, OnboardingJob, WorkspacePreferences

### 0.2 Infrastructure Setup ✅

#### 0.2.1 GCS Bucket Configuration ✅
- [x] Add GCS credentials bucket config to `src/core/config.py`
  - Field: gcs_credentials_bucket (optional, required for ConnectionService)
  - Field: gcs_credentials_prefix (default: "credentials/")
  - Note: Actual GCS bucket creation is deployment task, not code

#### 0.2.2 Cloud KMS Configuration ✅
- [x] Add Cloud KMS config to `src/core/config.py`
  - Fields: kms_key_ring, kms_crypto_key, kms_location (default: "global")
  - All optional, required when ConnectionService is initialized
  - Note: Actual KMS setup is deployment task, not code

#### 0.2.3 Environment Variables ✅
- [x] Added to settings.py: gcs_credentials_bucket, kms_key_ring, kms_crypto_key, kms_location
- [x] KMS/GCS clients integrated directly in ConnectionService (no separate wrappers needed)

### 0.3 Core Services ✅

#### 0.3.1 ConnectionService ✅
- [x] Create `src/services/connection.py` with ConnectionService class
- [x] Implement create_connection(team_id, name, connection_type, credentials)
  - Validates team exists
  - Encrypts credentials with Cloud KMS
  - Uploads encrypted credentials to GCS
  - Stores GCS path in Connection.credentials_path
  - Returns Connection with status="testing"
- [x] Implement test_connection(connection_id)
  - Downloads and decrypts credentials from GCS
  - Tests connection based on type (BigQuery/Postgres/Snowflake)
  - Updates status to "active" or "failed"
  - Returns success boolean
- [x] Implement get_connection(connection_id), list_connections(team_id)
- [x] Implement delete_connection(connection_id) - deletes GCS credentials + DB record
- [x] Implement get_decrypted_credentials(connection_id) for use by CatalogService
- [x] Enhanced: Multi-database testing methods (_test_bigquery_connection, _test_postgres_connection, _test_snowflake_connection)

#### 0.3.2 CatalogService ✅
- [x] Create `src/services/catalog.py` with CatalogService class
- [x] Implement discover_datasets(connection_id)
  - Queries metadata based on connection type
  - Creates/updates Dataset records
  - Returns list of discovered datasets
- [x] Implement scan_dataset_tables(dataset_id)
  - Updates dataset catalog_job_status to "running"
  - Scans tables from INFORMATION_SCHEMA or equivalent
  - Extracts schema metadata (columns, types, descriptions)
  - Stores schema in Table.schema JSONB field
  - Updates catalog_job_status to "completed" or "failed"
  - Returns list of tables
- [x] Implement get_dataset_tables(dataset_id), get_table_schema(table_id)
- [x] Enhanced: Multi-database discovery methods for BigQuery, Postgres, Snowflake

### 0.4 API Endpoints ✅

#### 0.4.1 Team Endpoints ✅
- [x] POST /v1/onboarding/teams - Create team
- [x] GET /v1/onboarding/teams/{team_id} - Get team details
- [x] GET /v1/onboarding/teams - List all teams

#### 0.4.2 Connection Endpoints ✅
- [x] POST /v1/onboarding/connections - Create connection
- [x] POST /v1/onboarding/connections/{connection_id}/test - Test connection
- [x] GET /v1/onboarding/connections?team_id={team_id} - List connections
- [x] GET /v1/onboarding/connections/{connection_id} - Get connection
- [x] DELETE /v1/onboarding/connections/{connection_id} - Delete connection

#### 0.4.3 Catalog Endpoints ✅
- [x] POST /v1/onboarding/catalog/discover?connection_id={id} - Discover datasets
- [x] POST /v1/onboarding/catalog/scan - Scan dataset tables
- [x] GET /v1/onboarding/catalog/datasets/{dataset_id}/tables - List tables
- [x] GET /v1/onboarding/catalog/tables/{table_id}/schema - Get table schema

**Files Created**:
- `apps/api/src/models/db_models.py` (Team, Connection, Dataset, Table models + enums)
- `apps/api/src/core/config.py` (GCS/KMS configuration)
- `apps/api/src/services/connection.py` (ConnectionService with KMS encryption)
- `apps/api/src/services/catalog.py` (CatalogService with multi-DB support)
- `apps/api/src/api/v1/onboarding.py` (10 API endpoints)
- `apps/api/alembic/versions/1ace71fc4600_add_onboarding_tables.py` (migration)

---

## Phase 3: API Endpoints ✅ COMPLETE

**Duration**: Completed 2025-10-30
**PDR Reference**: Backend PDR §3

### 3.1-3.10 Core API Endpoints
- [x] Dashboard CRUD endpoints
- [x] Data serving endpoints
- [x] Validation endpoints
- [x] Request/response models with Pydantic
- [x] Error handling and logging

**Note**: Chat API endpoints (Phase 3.11-3.13) are pending Phase 2.12 completion.

### 3.11 Chat Session Endpoints ⏳ PENDING

**Dependencies**: Phase 2.12 (Universal AI SDK)

#### 3.11.1 Session Management
- [ ] POST /v1/chat/sessions - Create new chat session
  - Body: {provider: "anthropic"}
  - Returns: {session_id, created_at}
- [ ] GET /v1/chat/sessions/{session_id} - Get session details
  - Returns: {session_id, messages[], total_tokens, status}
- [ ] DELETE /v1/chat/sessions/{session_id} - End session

#### 3.11.2 Streaming Chat
- [ ] POST /v1/chat/sessions/{session_id}/stream - Send message (SSE)
  - Body: {message: str, tools?: str[]}
  - Streams: event: token, event: tool_call, event: tool_result, event: done
  - Uses Universal AI SDK Orchestrator

#### 3.11.3 Session History
- [ ] GET /v1/chat/sessions - List user's sessions
- [ ] GET /v1/chat/sessions/{session_id}/messages - Get message history
- [ ] GET /v1/chat/sessions/{session_id}/export - Download GCS log

### 3.12 LLM Observability Endpoints (20 minutes)

**File**: `src/api/v1/observability.py`

- [ ] `GET /v1/observability/model-calls` - List model calls with filters
  - Query params: `?session_id=UUID`, `?provider=anthropic`, `?start_date=YYYY-MM-DD`, `?end_date=YYYY-MM-DD`, `?limit=100`, `?offset=0`
  - Response: Paginated list of `ModelCall` records
  - Status codes: 200 OK, 401 Unauthorized (admin only)
- [ ] `GET /v1/observability/cost-summary` - Aggregate LLM cost by user/session/time
  - Query params: `?user_id=UUID` (optional, defaults to current user), `?group_by=day|week|month` (default day)
  - Response: `{total_cost_usd: X.XX, total_tokens: N, breakdown: [{date, cost, tokens}, ...]}`
  - Status codes: 200 OK
- [ ] `GET /v1/observability/tool-cache-stats` - Cache efficiency metrics
  - Response: `{hit_rate_pct: XX.XX, total_hits: N, total_misses: M, total_cached_tools: K, storage_size_mb: X.X}`
  - Status codes: 200 OK

---

## Phase 3.5: Dashboard Generation via LLM 🎯 NEW - MVP BLOCKER

**Duration**: ~3 hours | **Priority**: CRITICAL
**PDR Reference**: Backend PDR §3.5 (to be added)
**Dependencies**: Phase 2.12 (Universal AI SDK), Phase 3.11 (Chat API)

### 3.5.1 BigQuery Tool (1 hour)

- [ ] Create `src/ai_sdk/tools/bigquery_tool.py`
- [ ] Implement list_datasets(connection_id) -> List[dict]
  - Query: SELECT schema_name, location FROM INFORMATION_SCHEMA.SCHEMATA
  - Returns: [{name, location, table_count}]
- [ ] Implement list_tables(dataset_name) -> List[dict]
  - Query: SELECT table_name, table_type, row_count, size_bytes FROM INFORMATION_SCHEMA.TABLES
  - Returns: [{name, type, row_count, size_mb}]
- [ ] Implement get_table_schema(table_name) -> dict
  - Query: SELECT column_name, data_type, is_nullable FROM INFORMATION_SCHEMA.COLUMNS
  - Returns: {table_name, columns: [{name, type, nullable}]}
- [ ] Implement run_dry_run_query(sql, max_bytes_billed=100_000_000) -> dict
  - Execute with dry_run=True
  - Returns: {bytes_scanned, estimated_cost, schema}
  - Error if bytes_scanned > max_bytes_billed

### 3.5.2 YAML Tool (30 minutes)

- [ ] Create `src/ai_sdk/tools/yaml_tool.py`
- [ ] Implement validate_dashboard_yaml(yaml_content) -> dict
  - Parse YAML with js-yaml
  - Validate against JSON Schema
  - Returns: {valid: bool, errors: []}
- [ ] Implement save_dashboard_yaml(yaml_content, slug, team_id) -> str
  - Upload to GCS: `gs://bridge-dashboards/{team_id}/{slug}.yaml`
  - Create Dashboard record in DB
  - Returns: gcs_path

### 3.5.3 Dashboard Generation Agent (1 hour)

- [ ] Create Dashboard model (SQLModel)
  - Fields: id, team_id, slug, title, description, gcs_yaml_path, owner_user_id, view_type, version, created_at, updated_at
  - Indexes: idx_team_dashboards, idx_dashboard_slug (unique per team)

- [ ] Create Alembic migration: `alembic revision --autogenerate -m "Add Dashboard model"`

- [ ] Create PromptBlock records for dashboard generation:
  - Block 1: YAML schema definition (cache_control: ephemeral)
  - Block 2: BigQuery best practices (partitioning, clustering, byte caps)
  - Block 3: Dashboard layout rules (12-column grid, monotone theme)

- [ ] Create `src/services/dashboard_generation_service.py`
- [ ] Implement generate_dashboard(session_id, user_message, connection_id) -> AsyncGenerator
  - Load prompt blocks
  - Load available datasets/tables from connection
  - Register tools: [bigquery_tool, yaml_tool]
  - Stream via Orchestrator.send_message()
  - Agent workflow:
    1. Explore schema (list_tables, get_table_schema)
    2. Propose SQL queries
    3. Run dry-run to verify bytes_scanned < 100 MB
    4. Generate YAML with layout
    5. Validate YAML
    6. Save to GCS + DB
  - Returns: {dashboard_slug, gcs_yaml_path, preview_url}

### 3.5.4 Dashboard Service & Acceptance Criteria (30 minutes)

- [ ] Update `src/services/dashboard_service.py`
  - Implement `async create_dashboard(team_id, slug, gcs_yaml_path, title, description, owner_user_id, view_type) -> Dashboard`
  - Implement `async get_dashboard(team_id, slug) -> Dashboard` (metadata + pointer only)
  - Implement `async list_dashboards(team_id, *, view_type=None, owner_user_id=None) -> List[Dashboard]`
  - Enforce pointer semantics: database stores slug + metadata, YAML body always lives in GCS
  - Validate slug uniqueness per team and surface conflict errors for frontend
- [ ] Add unit tests covering create/list/get flows and ensuring no YAML blobs are persisted in Postgres

**Acceptance Criteria**
- Agent MUST run a BigQuery dry-run and fail if `bytes_scanned >= 100 MB` before finalizing any SQL
- Agent MUST validate dashboard YAML against the JSON Schema before calling `save_dashboard_yaml`
- Agent SHOULD recommend partitioned queries whenever dry-run returns >1 GB scanned
- Agent SHOULD default to monotone (neutral grey) chart color palettes unless semantic colors are required

### 3.5.5 API Endpoints (30 minutes)

- [ ] POST /v1/dashboards/generate - Start dashboard generation
  - Body: {connection_id, user_prompt}
  - Creates new chat session
  - Streams SSE events
  - Returns: {session_id, dashboard_slug} on completion

- [ ] GET /v1/dashboards/{slug} - Get dashboard metadata
  - Returns: {slug, title, gcs_yaml_path, created_at}
  - Frontend fetches YAML from GCS separately

- [ ] GET /v1/teams/{team_id}/dashboards - List dashboards

---

## Phase 4: Dashboard Data Serving ⏳ PENDING

**Duration**: ~4 hours | **Priority**: HIGH
**PDR Reference**: Backend PDR §4
**Dependencies**: Phase 3.5 complete

### 4.1 Query Execution Service (2 hours)

- [ ] Create `src/services/query_execution_service.py`
- [ ] Implement execute_query(connection_id, sql, max_bytes_billed=100_000_000)
  - Download and decrypt BigQuery credentials from GCS
  - Initialize BigQuery client
  - Execute query with result cache enabled
  - Enforce byte cap (fail if exceeded)
  - Return compact JSON (arrays, not verbose objects)

- [ ] Implement cache strategy:
  - Key pattern: `dash:{slug}:q:{query_hash}:v:{version}`
  - TTL: 24-48 hours
  - Cache backend: Redis or in-process (configurable)

### 4.2 Dashboard Compiler (1 hour)

- [ ] Create `src/services/dashboard_compiler.py`
- [ ] Implement compile_dashboard(gcs_yaml_path) -> ExecutionPlan
  - Fetch YAML from GCS
  - Parse queries
  - Resolve dependencies between queries
  - Generate execution plan with parallelization hints
  - Returns: {queries: [{id, sql, dependencies}]}

### 4.3 Data Serving Endpoints (1 hour)

- [ ] GET /v1/dashboards/{slug}/data - Get all dashboard data
  - Load Dashboard record from DB → get gcs_yaml_path
  - Fetch and compile YAML
  - Execute all queries (parallel where possible)
  - Check cache first, execute if miss
  - Return: {queries: {q_id: {data, metadata}}}

- [ ] POST /v1/dashboards/{slug}/precompute - Warm cache
  - Admin/scheduled endpoint
  - Executes all queries and caches results
  - Returns: {queries_executed, cache_hits, errors}

- [ ] GET /v1/dashboards/{slug}/query/{query_id}/data - Get single query data
  - For on-demand filtering/drilling
  - Same cache strategy

---

## Phase 5: Observability & Testing ⏳ PENDING

**Duration**: ~3 hours | **Priority**: MEDIUM
**PDR Reference**: Backend PDR §5

### 5.1 OpenTelemetry Setup (1 hour)

- [ ] Add OpenTelemetry dependencies
- [ ] Configure tracing exporter
- [ ] Add spans for critical paths:
  - dashboard.compile
  - sql.execute
  - data.serve
  - precompute.run
  - chat.stream

- [ ] Add trace attributes:
  - dashboard_slug, query_hash, bytes_scanned, duration_ms, cache_hit

### 5.2 Structured Logging (30 minutes)

- [ ] Configure JSON logging format
- [ ] Add correlation IDs (x-correlation-id header)
- [ ] Error responses include trace_id

### 5.3 Testing (1.5 hours)

- [ ] Unit tests for services
- [ ] Integration tests for API endpoints
- [ ] Mock BigQuery for tests
- [ ] Test coverage: >80%

---

## Phase 6: Deployment & CI/CD ⏳ PENDING

**Duration**: ~2 hours | **Priority**: MEDIUM
**PDR Reference**: Backend PDR §6

### 6.1 Cloud Run Deployment

- [ ] Create Dockerfile (multi-stage build)
- [ ] Configure Cloud Run service
- [ ] Set up Cloud SQL proxy
- [ ] Configure Secret Manager integration

### 6.2 CI/CD Pipeline

- [ ] GitHub Actions workflow
  - Lint with ruff
  - Type check with mypy
  - Run tests
  - Build Docker image
  - Deploy to Cloud Run (on main push)

### 6.3 Database Migrations

- [ ] Automated migration on deployment
- [ ] Rollback strategy
- [ ] Backup policy

---

## Phase 6.5: YAML as Single Source of Truth Refactor ✅ COMPLETE

**Status**: ✅ COMPLETE (2025-10-31)  
**Actual Time**: 2 hours  
**Context**: Removed dual storage (YAML + Postgres) so dashboard YAML files are the source of truth. Database now stores only lightweight metadata pointers, eliminating YAML/DB drift risk and aligning with the "Postgres as directory, GCS as data lake" principle.

**Implementation Summary**
- YAML schema now carries owner, timestamps, and access counters
- StorageService no longer depends on SQLModel
- Lightweight `.index.json` accelerates dashboard listing/filtering
- REST endpoints read/write from filesystem only; rebuild endpoint available for ops

### 6.5.1 Update YAML Schema _(15 minutes)_ ✅
**File**: `src/models/yaml_schema.py`

- [x] Add `owner_email: str`, `created_at: datetime`, `updated_at: datetime`
- [x] Add `access_count: int = 0` and `last_accessed: Optional[datetime] = None`
- [x] Ensure backward compatibility with default values + validators

### 6.5.2 Refactor Storage Service _(1.5 hours)_ ✅
**File**: `src/services/storage.py`

- [x] Remove database dependencies and constructors that required `AsyncSession`
- [x] Ensure `save_dashboard()` enriches metadata, preserves original `created_at`, updates `.index.json`
- [x] Ensure `list_dashboards()` and `delete_dashboard()` operate solely on the filesystem + index
- [x] Implement `_read_index()`, `_update_index()`, `_remove_from_index()`, `_rebuild_index()` helpers
- [x] Simplify `record_access()` to edit YAML metadata in place

### 6.5.3 Update Dependencies _(5 minutes)_ ✅
**File**: `src/core/dependencies.py`

- [x] Remove DB injection from `get_storage_service`
- [x] Verify other services instantiate without breaking changes

### 6.5.4 Update API Endpoints _(30 minutes)_ ✅
**File**: `src/api/v1/dashboards.py`

- [x] `save_dashboard` now writes YAML + updates index, returns metadata without DB IDs
- [x] `list_dashboards` and `get_dashboard` read from index/YAML and still call `record_access`
- [x] Added `POST /v1/dashboards/rebuild-index` (admin only) to regenerate `.index.json`

### 6.5.5 Testing & Validation _(30 minutes)_ ✅

- [x] Exercised save/list/get/delete/rebuild endpoints manually end-to-end
- [x] Verified `.index.json` structure and automatic updates on mutations
- [x] Confirmed new schema fields populate correctly and no DB queries occur

---

## Phase X: Advanced Onboarding (Post-MVP) ⏸️ DEFERRED

**Duration**: ~20 hours | **Priority**: LOW - Deferred until cost guardrails established
**PDR Reference**: Backend PDR §X (to be created)

### X.1 Deferred Data Models & Jobs
- [ ] Reintroduce Column, PIIDetection, DbtArtifact, DocSource, GlossaryTerm, BusinessGoal, DataPolicy, OnboardingReport, OnboardingJob, WorkspacePreferences, TeamMember, TeamInvite models with the field definitions captured in backend_pdr.md §0
- [ ] Regenerate Alembic migrations for the deferred tables and related indexes (slug, status, foreign keys)
- [ ] Restore seed data + fixtures for advanced onboarding flows (PII samples, glossary snippets, governance policies)

### X.2 Deferred Services

#### X.2.1 PIIDetectorService _(2 hours)_
- [ ] Create `src/services/pii_detector_service.py` with asynchronous job orchestration
- [ ] Implement regex-based detectors for email, SSN, phone, credit card, name, address columns with configurable confidence thresholds
- [ ] Persist PIIDetection rows and expose approve/reject methods for manual review workflows

#### X.2.2 DbtService _(2 hours)_
- [ ] Implement manifest/catalog upload handlers with streaming parsing + type normalization
- [ ] Store parsed metadata in JSONB for lineage comparisons
- [ ] Add drift detection comparing dbt catalog vs INFORMATION_SCHEMA with partial-failure tolerance

#### X.2.3 DocCrawlerService _(3 hours)_
- [ ] Build async crawler with Confluence/Notion/internal adapters, rate limiting, and dedupe hashing
- [ ] Persist crawled pages to GCS and summarize counts per DocSource
- [ ] Add glossary extraction job that chunks docs, prompts Claude, and stores GlossaryTerm rows with confidence

#### X.2.4 LLMService _(1 hour)_
- [ ] Provide Anthropic client wrapper with retry, timeout, circuit breaker, and prompt redaction
- [ ] Support JSON-extraction helper with schema enforcement + query logging for cost tracking
- [ ] Gate concurrency per team to prevent runaway spend

#### X.2.5 OnboardingJobService _(1 hour)_
- [ ] Centralize job creation, progress updates, completion/failure helpers, and polling utilities for UI

#### X.2.6 BusinessGoalsService _(2 hours)_
- [ ] Implement goal mapping job that loads dataset metadata, prompts Claude with structured context, and stores BusinessGoal rows with reasoning + confidence

#### X.2.7 CostEstimatorService _(1 hour)_
- [ ] Compute heuristic cost projections plus dry-run verification jobs for the largest tables; enforce 1 GB safety threshold

#### X.2.8 ReportGeneratorService _(1 hour)_
- [ ] Assemble Markdown → HTML onboarding summary (exec summary, catalog, PII, governance, cost) and store OnboardingReport rows (HTML only, no PDF)

#### X.2.9 GovernanceService _(1 hour)_
- [ ] Generate masking + RLS policies from approved PIIDetections and persist DataPolicy entries for admin approval

#### X.2.10 LLM Platform Configuration & Safeguards _(1.5 hours)_
- [ ] Provide `llm_config.py` for model catalog, temperature ceilings, provider keys, and per-team rate limits
- [ ] Add prompt redaction + circuit breaker fallbacks per system_alignment.md

#### X.2.11 LLM Observability & QA _(2 hours)_
- [ ] Emit structured logs/metrics for each LLM call, add regression harness with mocked Anthropic responses, and document operational runbook

#### X.2.12 WorkspacePreferencesService _(30 minutes)_
- [ ] Infer defaults (analytical/operational/strategic view type, timezone, formats) from catalog metadata and persist WorkspacePreferences per team

### X.3 Deferred API Endpoints

#### X.3.1 PII Detection Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/pii.py`
- [ ] `POST /v1/onboarding/pii/detect` - Trigger PII detection (calls PIIDetectorService.detect_pii)
- [ ] `GET /v1/onboarding/pii/jobs/{job_id}` - Poll job status + progress payload
- [ ] `GET /v1/onboarding/pii/detections` - List pending detections with filters (connection_id, status)
- [ ] `POST /v1/onboarding/pii/detections/{id}/approve` and `/reject` - Manual review endpoints capturing reviewer + timestamp

#### X.3.2 dbt Integration Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/dbt.py`
- [ ] `POST /v1/onboarding/dbt/manifest` - Upload manifest.json (stream to GCS, parse, persist metadata)
- [ ] `POST /v1/onboarding/dbt/catalog` - Upload catalog.json (column-level lineage ingestion)
- [ ] `GET /v1/onboarding/dbt/drift` - Surface DbtService drift report (missing/extra/type mismatches)

#### X.3.3 Documentation & Glossary Endpoints _(1 hour)_
**File**: `src/api/v1/onboarding/docs.py`
- [ ] `POST /v1/onboarding/docs/crawl` + `GET /v1/onboarding/docs/jobs/{id}` for crawl orchestration
- [ ] `POST /v1/onboarding/docs/{doc_source_id}/glossary` - Trigger glossary extraction job
- [ ] `GET /v1/onboarding/glossary` - List GlossaryTerm rows with confidence filters

#### X.3.4 Business Goals Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/goals.py`
- [ ] `POST /v1/onboarding/goals/map` - Kick off goal mapping job
- [ ] `GET /v1/onboarding/goals/jobs/{id}` - Poll job status/results
- [ ] `GET /v1/onboarding/goals` - List mapped BusinessGoal entries with datasets, confidence, reasoning

#### X.3.5 Governance Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/governance.py`
- [ ] `POST /v1/onboarding/governance/policies` - Generate masking/RLS policies
- [ ] `GET /v1/onboarding/governance/policies` - List policies with filters (approved, connection_id)
- [ ] `POST /v1/onboarding/governance/policies/{policy_id}/approve` - Admin approval endpoint

#### X.3.6 Cost Estimation Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/cost.py`
- [ ] `GET /v1/onboarding/cost/estimate` - Return heuristic cost summary (cost_per_query, monthly estimate)
- [ ] `POST /v1/onboarding/cost/verify` + `GET /v1/onboarding/cost/jobs/{id}` - Dry-run verification job endpoints

#### X.3.7 Workspace Preferences Endpoints _(15 minutes)_
**File**: `src/api/v1/onboarding/preferences.py`
- [ ] `POST /v1/onboarding/preferences` - Generate defaults from WorkspacePreferencesService
- [ ] `GET /v1/onboarding/preferences` - Fetch stored preferences per team
- [ ] `PATCH /v1/onboarding/preferences/{id}` - Allow manual overrides

#### X.3.8 Onboarding Report Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/reports.py`
- [ ] `POST /v1/onboarding/reports` - Trigger HTML report generation (ReportGeneratorService)
- [ ] `GET /v1/onboarding/reports/{report_id}` - Retrieve stored report payload (HTML only, no PDF)

### X.4 Deferred Testing & Documentation _(2 hours)_
- [ ] Port Phase 0 unit tests (encryption, connection validation, catalog scan, PII regexes, dbt parsing, doc crawler rate limits, LLM JSON extraction, goal mapping, cost calc, report generation, governance rules)
- [ ] Reinstate API tests for onboarding routes plus full-flow integration test (team → connection → catalog → PII → report)
- [ ] Update OpenAPI spec + TS client with all onboarding endpoints, document encryption + PII patterns in backend_pdr.md, and refresh README onboarding instructions

**Rationale for Deferral**
- Violates "Postgres as directory, GCS as data lake" principle when shipped before dashboard generation path is proven
- Blocks MVP dashboard generation and adds 40+ endpoints + polling loops
- Requires cost guardrails + rate limits that are not yet defined
- Heavy LLM usage without observability/rate-limit circuit breakers
- Can be added incrementally post-MVP once Universal AI SDK + dashboard loop are stable

---

## Dependencies & Prerequisites

### External Services Required:
- PostgreSQL database
- Redis (optional, for cache)
- Google Cloud Storage (dashboards, credentials, logs)
- Google Cloud KMS (credential encryption)
- BigQuery (data warehouse)
- Anthropic API (Claude for LLM features)

### Environment Variables:
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/bridge
REDIS_URL=redis://localhost:6379/0
CREDENTIALS_BUCKET=gs://bridge-credentials-dev
DASHBOARDS_BUCKET=gs://bridge-dashboards-dev
KMS_KEY_NAME=projects/{PROJECT}/locations/us-central1/keyRings/bridge/cryptoKeys/credentials
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_CLOUD_PROJECT=bridge-project
```

---

**Last Updated**: 2025-11-12
**Next Priority**: Phase 0 (Minimal Onboarding) → Phase 2.12 (Universal AI SDK) → Phase 3.5 (Dashboard Generation)
