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
- **Phase 0**: ⏳ Pending (Minimal Team Onboarding)
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

## Phase 0: Minimal Team Onboarding ⏳ PENDING

**Duration**: ~4 hours | **Priority**: HIGH - Required before dashboard creation
**PDR Reference**: Backend PDR §0 (Trimmed per task_reorganization_plan.md)

**Philosophy**: Minimal models (4 tables), defer heavy onboarding to Phase X post-MVP.

### 0.1 Database Models & Migrations (1 hour)

#### 0.1.1 Team Model
- [ ] Create Team model (SQLModel)
  - Fields: id (UUID), name, slug, admin_user_id (FK to User), created_at, updated_at
  - Indexes: unique on slug

#### 0.1.2 Connection Model
- [ ] Create Connection model (SQLModel)
  - Fields: id, team_id (FK), name, warehouse_type (enum: bigquery), credentials_gcs_path, status (pending/validated/failed), validated_at, error_details, created_at, updated_at
  - Indexes: team_id

#### 0.1.3 Dataset Model
- [ ] Create Dataset model (SQLModel)
  - Fields: id, connection_id (FK), fully_qualified_name, description, location, last_modified, created_at
  - Indexes: connection_id, fully_qualified_name (unique per connection)

#### 0.1.4 Table Model
- [ ] Create Table model (SQLModel)
  - Fields: id, dataset_id (FK), fully_qualified_name, table_type, row_count, size_bytes, created_at, updated_at
  - Indexes: dataset_id, fully_qualified_name (unique per dataset)

#### 0.1.5 Migrations
- [ ] Create Alembic migration: `alembic revision --autogenerate -m "Phase 0: Minimal Onboarding Models"`
- [ ] Test migration up: `alembic upgrade head`
- [ ] Test migration down: `alembic downgrade -1`
- [ ] Seed test data: Sample Team, Connection, Dataset, Table

**Deferred Models** (to Phase X post-MVP):
- Column, PIIDetection, DbtArtifact, DocSource, GlossaryTerm, BusinessGoal, DataPolicy, OnboardingReport, OnboardingJob, WorkspacePreferences

### 0.2 Infrastructure Setup (1 hour)

#### 0.2.1 GCS Bucket
- [ ] Create GCS bucket: `gs://bridge-credentials-{env}/`
- [ ] Configure lifecycle: 90-day retention for service account files
- [ ] Set IAM permissions: API service account has Storage Object Admin

#### 0.2.2 Cloud KMS
- [ ] Create key ring: `projects/{PROJECT}/locations/us-central1/keyRings/bridge-credentials`
- [ ] Create crypto key: `bridge-credentials/cryptoKeys/service-account-encryption`
- [ ] Configure rotation policy: 90 days
- [ ] Set IAM: API service account has CryptoKey Encrypter/Decrypter

#### 0.2.3 Environment Variables
- [ ] Add to settings.py: CREDENTIALS_BUCKET, KMS_KEY_NAME
- [ ] Create `src/core/gcs.py` with GCS client wrapper
- [ ] Create `src/core/kms.py` with KMS client wrapper

### 0.3 Core Services (1.5 hours)

#### 0.3.1 EncryptionService
- [ ] Create `src/services/encryption_service.py`
- [ ] Implement encrypt(plaintext: bytes) -> bytes
- [ ] Implement decrypt(ciphertext: bytes) -> bytes
- [ ] Add error handling for KMS quota, invalid ciphertext

#### 0.3.2 ConnectionService
- [ ] Create `src/services/connection_service.py`
- [ ] Implement create_connection(team_id, name, warehouse_type, credentials_file)
  - Validate JSON structure (project_id, client_email, private_key)
  - Encrypt credentials, upload to GCS
  - Store GCS path in Connection.credentials_gcs_path
  - Set status to "pending_validation"
- [ ] Implement validate_connection(connection_id)
  - Download and decrypt credentials
  - Initialize BigQuery client
  - Run test query: SELECT 1 (dry_run=True, 0 bytes)
  - Check permissions: datasets.list, tables.list, jobs.create
  - Update status to "validated" or "failed"
- [ ] Implement list_connections(team_id), delete_connection(connection_id)

#### 0.3.3 CatalogService (Lightweight)
- [ ] Create `src/services/catalog_service.py`
- [ ] Implement scan_datasets(connection_id)
  - Query INFORMATION_SCHEMA.SCHEMATA for datasets
  - Query INFORMATION_SCHEMA.TABLES for tables (no columns in MVP)
  - Create/update Dataset and Table records
  - Return counts: {datasets: N, tables: M}
- [ ] No async jobs in MVP (synchronous scan only)

### 0.4 API Endpoints (30 minutes)

#### 0.4.1 Team Endpoints
- [ ] POST /v1/teams - Create team
- [ ] GET /v1/teams/{team_id} - Get team details
- [ ] GET /v1/teams - List user's teams

#### 0.4.2 Connection Endpoints
- [ ] POST /v1/teams/{team_id}/connections - Create connection
- [ ] POST /v1/connections/{connection_id}/validate - Validate connection
- [ ] GET /v1/teams/{team_id}/connections - List connections
- [ ] DELETE /v1/connections/{connection_id} - Delete connection

#### 0.4.3 Catalog Endpoints
- [ ] POST /v1/connections/{connection_id}/scan - Trigger catalog scan
- [ ] GET /v1/connections/{connection_id}/datasets - List datasets
- [ ] GET /v1/datasets/{dataset_id}/tables - List tables

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

### 3.5.4 API Endpoints (30 minutes)

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

## Phase X: Advanced Onboarding (Post-MVP) ⏸️ DEFERRED

**Duration**: ~20 hours | **Priority**: LOW - Deferred until cost guardrails established
**PDR Reference**: Backend PDR §X (to be created)

### Models to Add (13 tables):
- Column, PIIDetection, DbtArtifact, DocSource, GlossaryTerm, BusinessGoal, DataPolicy, OnboardingReport, OnboardingJob, WorkspacePreferences, TeamMember, TeamInvite

### Services to Add:
- PIIDetectorService (Claude-powered PII scanning)
- DbtService (parse manifest/catalog, drift detection)
- DocCrawlerService (Confluence/Notion crawling)
- GlossaryService (term extraction with Claude)
- BusinessGoalsService (goal-to-data mapping)
- PolicyGenerationService (RLS/masking policies)
- CostEstimatorService (query cost prediction)
- ReportGeneratorService (HTML onboarding reports)
- GovernanceService (policy enforcement)

**Rationale for Deferral**:
- Violates "Postgres as directory, GCS as data lake" principle
- Blocks MVP dashboard generation
- Requires cost guardrails not yet defined
- Heavy LLM usage without rate limits
- Can be added incrementally post-MVP

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
