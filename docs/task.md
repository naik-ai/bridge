# Backend Implementation Tasks

## Phase 0: Team Onboarding & Data Source Setup
**Duration**: Weeks 1-2 (parallel to MVP foundation)
**Priority**: Pre-MVP - Required before dashboard creation
**PDR Reference**: Backend PDR §0 (Team Onboarding)

**Phase 0 Status**: ⏳ PENDING

### 0.1 Database Models & Migrations (PDR §0.1)
- [ ] 0.1.1 Create Team model (SQLModel) with fields: id, name, slug, admin_user_id, settings, onboarding_completed, timestamps
- [ ] 0.1.2 Create TeamMember model (join table) with role field (admin/editor/viewer)
- [ ] 0.1.3 Create TeamInvite model with invite_token, expires_at, accepted_at
- [ ] 0.1.4 Update User model to add relationships: owned_teams, team_memberships
- [ ] 0.1.5 Create Connection model (BigQuery) with encrypted credentials path, validation status, warehouse_type
- [ ] 0.1.6 Create Dataset model with fully_qualified_name, description, location, labels (JSONB), last_modified
- [ ] 0.1.7 Create Table model with dataset_id FK, fully_qualified_name, table_type, row_count, size_bytes, partitioning, clustering
- [ ] 0.1.8 Create Column model with table_id FK, name, data_type, is_nullable, description, ordinal_position
- [ ] 0.1.9 Create PIIDetection model with column_id FK, pattern_name, confidence_score, status (pending/approved/rejected), reviewed_by, reviewed_at
- [ ] 0.1.10 Create DbtArtifact model with connection_id FK, artifact_type (manifest/catalog), uploaded_at, file_path, parsed_metadata (JSONB)
- [ ] 0.1.11 Create DocSource model with connection_id FK, source_type (confluence/notion/internal), base_url, crawled_at, page_count
- [ ] 0.1.12 Create GlossaryTerm model with doc_source_id FK, term, definition, related_datasets (array), confidence_score
- [ ] 0.1.13 Create BusinessGoal model with team_id FK, goal_text, mapped_datasets (JSONB array), confidence_scores (JSONB), created_by
- [ ] 0.1.14 Create WorkspacePreferences model with team_id FK (unique), default_view_type, date_format, timezone, number_format, theme, settings (JSONB)
- [ ] 0.1.15 Create DataPolicy model with dataset_id FK, policy_type (masking/rls), column_name, policy_sql, reason, approved
- [ ] 0.1.16 Create OnboardingReport model with team_id FK, report_html, checklist_items (JSONB), stats (JSONB), generated_at (NOTE: No PDF path field - PDF generation removed)
- [ ] 0.1.17 Create OnboardingJob model with team_id FK, job_type (catalog/pii/dbt/docs/goals/verification), status, progress (0-100), result (JSONB), error, started_at, completed_at
- [ ] 0.1.18 Add indexes on Team.slug, Connection.team_id, Dataset.connection_id, Table.dataset_id, Column.table_id, PIIDetection.status
- [ ] 0.1.19 Create Alembic migration for all Phase 0 models: `alembic revision --autogenerate -m "Phase 0: Team Onboarding Schema"`
- [ ] 0.1.20 Test migration up: `alembic upgrade head` (verify all tables created)
- [ ] 0.1.21 Test migration down: `alembic downgrade -1` (verify rollback works)
- [ ] 0.1.22 Seed test data: Create sample Team, Connection, Dataset, Table, Column records for local development
- [ ] 0.1.23 Review fee-admin standalone auth/team implementation (`/Users/jaynaik/Desktop/bdlabs/fee-admin-standalone/backend`) for reusable OAuth + team membership patterns
- [ ] 0.1.24 Catalog reusable modules (OAuth routes, session middleware, team role enforcement) and document adaptation steps for Phase 0
- [ ] 0.1.25 Create integration plan doc (Phase 0) outlining which components will be imported vs rewritten, including risk notes

### 0.2 Infrastructure Setup - Cloud KMS & GCS (PDR §0.2)
- [ ] 0.2.1 Create GCS bucket for onboarding artifacts: `gs://peter-onboarding-{env}/`
- [ ] 0.2.2 Configure GCS bucket lifecycle: 90-day retention for service account files, no expiration for reports
- [ ] 0.2.3 Set GCS IAM permissions: API service account has Storage Object Admin role
- [ ] 0.2.4 Create Cloud KMS key ring: `projects/{PROJECT_ID}/locations/us-central1/keyRings/peter-onboarding`
- [ ] 0.2.5 Create Cloud KMS crypto key: `peter-onboarding/cryptoKeys/service-account-encryption`
- [ ] 0.2.6 Configure KMS key rotation policy: 90 days
- [ ] 0.2.7 Set KMS IAM permissions: API service account has Cloud KMS CryptoKey Encrypter/Decrypter role
- [ ] 0.2.8 Add environment variables: ONBOARDING_BUCKET, KMS_KEY_NAME to config.py
- [ ] 0.2.9 Create `src/core/gcs.py` with GCS client wrapper (upload, download, delete, list methods)
- [ ] 0.2.10 Create `src/core/kms.py` with KMS client wrapper (encrypt, decrypt methods)
- [ ] 0.2.11 Store Anthropic API key in Secret Manager: `projects/{PROJECT_ID}/secrets/anthropic-api-key`
- [ ] 0.2.12 Add Secret Manager read permissions for API service account
- [ ] 0.2.13 Store Confluence API token in Secret Manager: `projects/{PROJECT_ID}/secrets/confluence-api-token`
- [ ] 0.2.14 Store Notion API token in Secret Manager: `projects/{PROJECT_ID}/secrets/notion-api-token`
- [ ] 0.2.15 Add environment variables: ANTHROPIC_API_KEY_SECRET, CONFLUENCE_TOKEN_SECRET, NOTION_TOKEN_SECRET to config.py

### 0.3 Core Services Implementation (PDR §0.3-0.11)

#### 0.3.1 KMS & GCS Services _(1 hour)_
- [ ] Create `src/services/encryption_service.py` with EncryptionService class
- [ ] Implement `encrypt(plaintext: bytes) -> bytes` method (calls Cloud KMS)
- [ ] Implement `decrypt(ciphertext: bytes) -> bytes` method (calls Cloud KMS)
- [ ] Add error handling for KMS quota exhaustion, invalid ciphertext
- [ ] Create `src/services/storage_service.py` (onboarding-specific, not dashboard storage)
- [ ] Implement `upload_service_account(team_slug: str, file: UploadFile) -> str` (returns GCS path)
- [ ] Implement `download_service_account(gcs_path: str) -> bytes` method
- [ ] Implement `upload_dbt_artifact(team_slug: str, artifact_type: str, file: UploadFile) -> str` method
- [ ] Implement `upload_report(team_slug: str, report_html: str) -> str` (returns HTML GCS path only - no PDF)
- [ ] Add unit tests for encryption round-trip, GCS upload/download

#### 0.3.2 Connection Service _(2 hours)_
- [ ] Create `src/services/connection_service.py` with ConnectionService class
- [ ] Implement `async create_connection(team_id, name, warehouse_type, credentials_file) -> Connection`
  - Validate JSON structure (has project_id, client_email, private_key)
  - Encrypt credentials using EncryptionService
  - Upload encrypted file to GCS
  - Store GCS path in Connection.credentials_path
  - Set status to "pending_validation"
- [ ] Implement `async validate_connection(connection_id: UUID) -> dict` method
  - Download and decrypt credentials from GCS
  - Initialize BigQuery client with credentials
  - Run test query: `SELECT 1` (dry_run=True, 0 bytes billed)
  - Check permissions: datasets.list, tables.list, jobs.create (required)
  - Update Connection.status to "validated" or "failed" with error details
- [ ] Implement `async list_connections(team_id: UUID) -> List[Connection]` method
- [ ] Implement `async delete_connection(connection_id: UUID)` method (removes GCS file, DB record)
- [ ] Add error handling for malformed JSON, insufficient permissions, network errors

#### 0.3.3 Catalog Scanner Service _(3 hours)_
- [ ] Create `src/services/catalog_service.py` with CatalogService class
- [ ] Implement `async scan_datasets(connection_id: UUID) -> OnboardingJob` method
  - Creates OnboardingJob with type "catalog", status "running"
  - Runs asynchronously via background task or Celery (MVP: async task)
  - Returns job immediately for polling
- [ ] Implement `async _execute_catalog_scan(job_id: UUID, connection_id: UUID)` background method
  - Download and decrypt BigQuery credentials
  - Query INFORMATION_SCHEMA.SCHEMATA: `SELECT schema_name, location, creation_time FROM project_id.region-us.INFORMATION_SCHEMA.SCHEMATA`
  - Create Dataset records (or update if exists)
  - Query INFORMATION_SCHEMA.TABLES: `SELECT table_catalog, table_schema, table_name, table_type, creation_time FROM project_id.region-us.INFORMATION_SCHEMA.TABLES`
  - Create Table records with row_count, size_bytes from INFORMATION_SCHEMA.TABLE_STORAGE
  - Query INFORMATION_SCHEMA.COLUMNS: `SELECT table_name, column_name, ordinal_position, is_nullable, data_type FROM project_id.region-us.INFORMATION_SCHEMA.COLUMNS`
  - Create Column records
  - Update job status to "completed", set result JSON with counts: {datasets: N, tables: M, columns: K}
  - On error: Set job status to "failed", store error message
- [ ] Implement `async get_job_status(job_id: UUID) -> OnboardingJob` method (for polling)
- [ ] Add progress tracking: Update job.progress field incrementally (0-100%)
- [ ] Add unit tests with mocked BigQuery client

#### 0.3.4 PII Detector Service _(2 hours)_
- [ ] Create `src/services/pii_detector_service.py` with PIIDetectorService class
- [ ] Implement `async detect_pii(connection_id: UUID) -> OnboardingJob` method (returns job for polling)
- [ ] Implement `async _execute_pii_detection(job_id: UUID, connection_id: UUID)` background method
  - Load all Column records for connection's datasets
  - Apply regex patterns to column names and data_type:
    - Email: `r'email|e_mail|mail_address'` (case insensitive) → confidence 0.9
    - SSN: `r'ssn|social_security|social_sec'` → confidence 0.85
    - Phone: `r'phone|telephone|mobile|cell'` → confidence 0.8
    - Credit Card: `r'credit_card|cc_number|card_num'` → confidence 0.9
    - Name: `r'(first_name|last_name|full_name|customer_name)'` → confidence 0.7
    - Address: `r'address|street|city|zip|postal'` → confidence 0.6
  - Create PIIDetection records with pattern_name, confidence_score, status="pending" if score < 0.7, status="approved" if >= 0.7
  - Update job result: {total_columns: N, pii_detected: M, auto_approved: K, manual_review: L}
  - Set job status to "completed"
- [ ] Implement `async approve_pii_detection(detection_id: UUID, user_id: UUID)` method (manual review)
- [ ] Implement `async reject_pii_detection(detection_id: UUID, user_id: UUID)` method
- [ ] Add unit tests for each regex pattern

#### 0.3.5 dbt Integration Service _(2 hours)_
- [ ] Create `src/services/dbt_service.py` with DbtService class
- [ ] Create dbt-to-BigQuery type mapping dictionary: {STRING: STRING, INT64: INTEGER, FLOAT64: FLOAT, BOOL: BOOLEAN, etc.}
- [ ] Implement `async upload_manifest(connection_id: UUID, manifest_file: UploadFile) -> DbtArtifact` method
  - Validate dbt version compatibility (support 1.0+, check metadata.dbt_version)
  - Validate JSON structure (has nodes, sources keys)
  - Implement streaming parser for large files (>10 MB): Read in 1 MB chunks, parse incrementally
  - Upload to GCS: `gs://{bucket}/{team_slug}/dbt/manifest_{timestamp}.json`
  - Parse manifest: Extract model names, dependencies, source tables
  - Store parsed_metadata JSONB: {models: [...], sources: [...], dependencies: [...], dbt_version: "1.5.0"}
  - Create DbtArtifact record
- [ ] Implement `async upload_catalog(connection_id: UUID, catalog_file: UploadFile) -> DbtArtifact` method
  - Validate JSON structure (has nodes key)
  - Parse catalog: Extract column-level lineage, descriptions, data types
  - Normalize dbt data types to BigQuery types using mapping dictionary
  - Store parsed_metadata JSONB
- [ ] Implement `async detect_drift(connection_id: UUID) -> dict` method
  - Compare dbt catalog columns with INFORMATION_SCHEMA columns
  - Normalize both dbt and BigQuery types before comparison (handle STRING vs VARCHAR, INT64 vs INTEGER)
  - Identify: missing columns in dbt, extra columns in warehouse, type mismatches
  - Return drift report: {missing: [...], extra: [...], type_mismatches: [...], partial_failures: [...]}
  - Continue processing even if one table has drift (partial failure handling)
- [ ] Add error handling for invalid JSON, missing required keys, unsupported dbt versions

#### 0.3.6 Documentation Crawler Service _(3 hours)_
- [ ] Create `src/services/doc_crawler_service.py` with DocCrawlerService class
- [ ] Add dependencies to requirements.txt: html2text, markdownify
- [ ] Implement `async crawl_docs(connection_id: UUID, base_url: str, source_type: str, auth_token: str) -> OnboardingJob` method
  - Create OnboardingJob with type "docs", status "running"
  - Returns job for polling
- [ ] Implement `async _execute_doc_crawl(job_id: UUID, connection_id: UUID, base_url: str, source_type: str, auth_token: str)` background method
  - Initialize httpx.AsyncClient with connection pooling (max 10 connections)
  - Rate limit: 10 pages/minute (asyncio.Semaphore(1) with 6 second delay between requests)
  - For Confluence: Use REST API v2 `/wiki/api/v2/spaces/{space_key}/pages`
    - Authentication: Bearer token from Secret Manager
    - Extract: page.title, page.body.storage.value (convert Confluence storage format to markdown)
    - Pagination: Follow _links.next until exhausted
  - For Notion: Use Notion API v1 `/v1/search`
    - Authentication: Notion-Version: 2022-06-28, Bearer token
    - Recursive page traversal with max_depth parameter
    - Convert blocks to markdown using custom renderer
  - For internal docs: HTTP GET on sitemap.xml or index.json
    - Convert HTML to markdown using html2text library
  - Calculate content hash (SHA256) for deduplication
  - Check if content_hash exists in previous crawls; skip if duplicate
  - Store in GCS: `gs://{bucket}/{team_slug}/docs/{source_type}/{content_hash}.md`
  - Track last_crawled timestamp per page URL for incremental updates
  - Create DocSource record with page_count
  - Update job result: {pages_crawled: N, total_pages: M, duplicates_skipped: K}
  - Partial failure handling: Continue crawling remaining pages even if some fail
  - Set job status to "completed"
- [ ] Implement `async extract_glossary(doc_source_id: UUID) -> OnboardingJob` method (calls LLM)
- [ ] Implement `async _execute_glossary_extraction(job_id: UUID, doc_source_id: UUID)` background method
  - Load all page content from GCS
  - Chunk pages into 10KB segments (handle context window limits)
  - For each chunk, call LLM (Claude API) with prompt:
    ```
    Extract data glossary terms from this documentation. Return JSON array:
    [{"term": "...", "definition": "...", "related_datasets": ["project.dataset.table", ...]}]
    Only include terms that reference specific data tables or columns.
    ```
  - Parse LLM response JSON
  - Calculate confidence_score based on specificity of definition (0.0-1.0)
  - Create GlossaryTerm records
  - Update job result: {terms_extracted: N}
- [ ] Add error handling for API rate limits (429), authentication failures (401), LLM timeout (30s), network errors

#### 0.3.7 LLM Service _(1 hour)_
- [ ] Create `src/services/llm_service.py` with LLMService class (wrapper for Anthropic Claude API)
- [ ] Load Anthropic API key from Secret Manager with environment variable fallback
- [ ] Create prompt template management system with versioning (store in config or JSONB)
- [ ] Implement `async generate_completion(prompt: str, max_tokens: int, temperature: float) -> str` method
  - Initialize anthropic.Anthropic client with API key from Secret Manager
  - Apply PII redaction pre-processor (scrub emails, SSNs before sending to LLM)
  - Call messages.create() with claude-3-5-sonnet-20241022 model
  - Handle rate limits with exponential backoff (3 retries, @retry_async decorator)
  - Add timeout: 30 seconds
  - Emit structured logs: prompt_hash, token_usage, latency, model, status (no raw content)
  - Track token usage for cost calculation
- [ ] Implement `async extract_json(prompt: str, schema: dict) -> dict` method
  - Adds JSON schema constraint to prompt
  - Parses response, validates against schema using jsonschema library
  - Returns parsed JSON or raises validation error
- [ ] Add QueryLog integration: Create QueryLog record for each LLM call with purpose="llm_glossary" or "llm_goals"
  - Store: input_tokens, output_tokens, duration_ms, model, cost estimate ($3 per 1M input tokens, $15 per 1M output tokens)
- [ ] Implement context window management: Split large inputs (>100KB) into chunks, call LLM separately, merge results
- [ ] Add concurrency guard: AsyncIO semaphore limiting concurrent LLM calls to 5 per team
- [ ] Implement circuit breaker: After 5 consecutive failures, stop calling LLM for 5 minutes, return cached/empty results

#### 0.3.8 Onboarding Job Service _(1 hour)_
- [ ] Create `src/services/onboarding_job_service.py` with OnboardingJobService class
- [ ] Implement `async create_job(team_id: UUID, job_type: str) -> OnboardingJob` method
  - Creates OnboardingJob with status "pending"
  - Returns job record
- [ ] Implement `async get_job(job_id: UUID) -> OnboardingJob` method (for polling)
- [ ] Implement `async update_progress(job_id: UUID, progress: int)` method (0-100)
- [ ] Implement `async complete_job(job_id: UUID, result: dict)` method (sets status "completed", stores result JSON)
- [ ] Implement `async fail_job(job_id: UUID, error: str)` method (sets status "failed", stores error message)
- [ ] Implement `async list_jobs(team_id: UUID, job_type: Optional[str]) -> List[OnboardingJob]` method

#### 0.3.9 Business Goals Mapping Service _(2 hours)_
- [ ] Create `src/services/business_goals_service.py` with BusinessGoalsService class
- [ ] Implement `async map_goals(connection_id: UUID, goals: List[str]) -> OnboardingJob` method
  - Create OnboardingJob with type "goals", status "running"
  - Returns job for polling
- [ ] Implement `async _execute_goal_mapping(job_id: UUID, connection_id: UUID, goals: List[str])` background method
  - Load all Dataset and Table records for connection
  - For each goal text:
    - Build context: List of available tables with column names and descriptions
    - Call LLM with prompt:
      ```
      Business goal: "{goal_text}"
      Available datasets: {table_list_with_columns}

      Identify which datasets/tables are relevant to answering this business question.
      Return JSON: {"relevant_tables": ["project.dataset.table", ...], "confidence": 0.0-1.0, "reasoning": "..."}
      ```
    - Parse LLM response
    - Create BusinessGoal record with mapped_datasets, confidence_scores
  - Update job result: {goals_mapped: N, avg_confidence: X}
  - Set job status to "completed"
- [ ] Add error handling for LLM failures, invalid goal text

#### 0.3.10 Cost Estimation Service _(1 hour)_
- [ ] Create `src/services/cost_estimator_service.py` with CostEstimatorService class
- [ ] Implement `async estimate_dashboard_costs(connection_id: UUID) -> dict` method
  - Load all Table records with size_bytes
  - Assume typical query scans 10% of table data
  - Calculate: bytes_scanned_per_query = sum(table.size_bytes * 0.1) for top 10 tables
  - Apply BigQuery pricing: $5 per TB
  - Estimate: cost_per_query_usd = (bytes_scanned_per_query / 1e12) * 5
  - Estimate monthly cost: Assume 10 dashboards × 100 queries/day × 30 days
  - Return: {cost_per_query: X, estimated_monthly: Y, bytes_scanned_per_query: Z}
- [ ] Implement `async run_verification_queries(connection_id: UUID) -> OnboardingJob` method
  - Create OnboardingJob with type "verification", status "running"
  - Returns job for polling
- [ ] Implement `async _execute_verification_queries(job_id: UUID, connection_id: UUID)` background method
  - Select top 5 largest tables
  - For each table: Run dry-run query `SELECT * FROM {table} LIMIT 100` with dry_run=True
  - Record bytes_billed (should be 0), bytes_scanned (from job statistics)
  - Verify: bytes_scanned < 1 GB (safety threshold)
  - Update job result: {tables_verified: N, total_bytes_scanned: X}
  - Set job status to "completed"

#### 0.3.11 Report Generator Service _(1 hour)_ - HTML Summary Only
- [ ] Create `src/services/report_generator_service.py` with ReportGeneratorService class
- [ ] Implement `async generate_report(team_id: UUID) -> OnboardingReport` method
  - Load Team, Connection, Dataset, Table, PIIDetection, BusinessGoal records
  - Build Markdown report with sections:
    1. Executive Summary (team name, connection count, dataset count)
    2. Data Catalog Overview (table with dataset names, table counts, total size)
    3. PII Detection Results (table with column names, pattern, confidence, status)
    4. Business Goals (table with goal text, mapped datasets, confidence)
    5. Governance Recommendations (masking policies for PII columns)
    6. Cost Estimates (monthly query cost projection)
    7. Checklist (10 items: connection validated ✓, catalog scanned ✓, PII reviewed ✓, etc.)
  - Render Markdown to HTML using markdown library
  - Create OnboardingReport record with report_html, checklist_items, stats
  - NOTE: No PDF generation for MVP (removed per user request)
- [ ] Add unit tests with mocked data

#### 0.3.12 Governance Service _(1 hour)_
- [ ] Create `src/services/governance_service.py` with GovernanceService class
- [ ] Implement `async generate_policies(connection_id: UUID) -> List[DataPolicy]` method
  - Load PIIDetection records with status "approved"
  - For each PII column:
    - If pattern is "email", create masking policy: `REGEXP_REPLACE(email, r'@.*', '@*****.com')`
    - If pattern is "ssn", create masking policy: `CONCAT('XXX-XX-', SUBSTR(ssn, -4, 4))`
    - If pattern is "credit_card", create masking policy: `CONCAT('****-****-****-', SUBSTR(cc, -4, 4))`
    - Create DataPolicy record with policy_type "masking", column_name, policy_sql, reason, approved=False (requires admin approval)
  - For tables with sensitive data, recommend RLS policies:
    - policy_sql: `WHERE user_email = SESSION_USER()` (row-level filtering)
    - Create DataPolicy record with policy_type "rls", approved=False
  - Return list of generated policies

#### 0.3.13 LLM Platform Configuration & Safeguards _(1.5 hours)_
- [ ] Create `src/core/llm_config.py` (model catalog, temperature defaults, token ceilings, feature flags)
- [ ] Load provider API keys + org IDs from Secret Manager; expose via settings with environment fallbacks
- [ ] Add concurrency guard (async semaphore) + per-team rate limiter inside LLMService
- [ ] Implement redaction pre-processor to scrub emails/SSNs from prompts before provider call
- [ ] Define failure policy: circuit breaker after 5 consecutive errors, fallback to cached glossary/goal outputs

#### 0.3.14 LLM Observability & QA _(2 hours)_
- [ ] Emit structured logs for each LLM call (prompt hash, token usage, latency, model, status) without leaking raw content
- [ ] Publish metrics: `llm_requests_total`, `llm_tokens_input`, `llm_tokens_output`, `llm_failures_total`
- [ ] Build offline regression harness with mocked Anthropic responses to validate JSON parsing + schema enforcement
- [ ] Create synthetic evaluation dataset (5 glossary docs, 5 goal prompts) and snapshot expected outputs for CI regression
- [ ] Document operational runbook covering key rotation, quota monitoring, provider outage playbook

#### 0.3.15 Workspace Preferences Service _(30 minutes)_
- [ ] Create `src/services/workspace_preferences_service.py` with WorkspacePreferencesService class
- [ ] Implement `async generate_preferences(team_id: UUID, connection_id: UUID) -> WorkspacePreferences` method
  - Load Dataset, Table records
  - Infer default_view_type based on data patterns:
    - If tables have "fact_" prefix or star schema detected → "analytical"
    - If tables have "real_time" or "streaming" in name → "operational"
    - If tables have "_summary" or "_kpi" suffix → "strategic"
  - Infer timezone from BigQuery dataset location (us-central1 → America/Chicago)
  - Set defaults: date_format="YYYY-MM-DD", number_format="1,234.56", theme="light"
  - Create WorkspacePreferences record (unique per team)
- [ ] Implement `async update_preferences(team_id: UUID, preferences: dict) -> WorkspacePreferences` method (manual overrides)

### 0.4 API Endpoints (PDR §0.12)

#### 0.4.1 Team Management Endpoints _(1 hour)_
**File**: `src/api/v1/onboarding/teams.py`
- [ ] `POST /v1/onboarding/teams` - Create new team (first user becomes admin)
  - Request: {name: str}
  - Generates slug from name (lowercase, hyphenated)
  - Links user to team via TeamMember with role "admin"
  - Response: {team_id, slug, name, admin_user_id, created_at}
- [ ] `GET /v1/onboarding/teams/{team_id}` - Get team details
  - Response: {id, name, slug, admin_user_id, members: [{user_id, email, role}], onboarding_completed, settings}
- [ ] `PATCH /v1/onboarding/teams/{team_id}` - Update team settings
  - Request: {name?, settings?: {...}}
  - Response: Updated team object
- [ ] `POST /v1/onboarding/teams/{team_id}/members` - Invite user to team
  - Request: {email: str, role: "admin"|"editor"|"viewer"}
  - Creates TeamInvite with 7-day expiration
  - Sends invite email (stub for MVP)
  - Response: {invite_id, email, role, invite_token, expires_at}
- [ ] `DELETE /v1/onboarding/teams/{team_id}/members/{user_id}` - Remove member

#### 0.4.2 Connection Endpoints _(1 hour)_
**File**: `src/api/v1/onboarding/connections.py`
- [ ] `POST /v1/onboarding/connections` - Create BigQuery connection
  - Request: Multipart form data {team_id, name, warehouse_type: "bigquery", credentials: File}
  - Calls ConnectionService.create_connection()
  - Response: {connection_id, name, status: "pending_validation", created_at}
- [ ] `POST /v1/onboarding/connections/{connection_id}/validate` - Trigger connection validation
  - Calls ConnectionService.validate_connection()
  - Response: {connection_id, status: "validated"|"failed", error?: str, validated_at}
- [ ] `GET /v1/onboarding/connections` - List connections for team
  - Query params: ?team_id=...
  - Response: [{connection_id, name, status, warehouse_type, created_at}, ...]
- [ ] `DELETE /v1/onboarding/connections/{connection_id}` - Delete connection (also removes GCS file)

#### 0.4.3 Catalog Endpoints _(1 hour)_
**File**: `src/api/v1/onboarding/catalog.py`
- [ ] `POST /v1/onboarding/catalog/scan` - Trigger catalog scan
  - Request: {connection_id}
  - Calls CatalogService.scan_datasets()
  - Response: {job_id, status: "running", created_at}
- [ ] `GET /v1/onboarding/catalog/jobs/{job_id}` - Get catalog scan job status (polling endpoint)
  - Response: {job_id, status, progress, result?: {datasets: N, tables: M, columns: K}, error?, completed_at?}
- [ ] `GET /v1/onboarding/catalog/datasets` - List datasets for connection
  - Query params: ?connection_id=...
  - Response: [{dataset_id, fully_qualified_name, table_count, size_bytes, last_modified}, ...]
- [ ] `GET /v1/onboarding/catalog/datasets/{dataset_id}/tables` - List tables in dataset
  - Response: [{table_id, fully_qualified_name, table_type, row_count, size_bytes, column_count}, ...]
- [ ] `GET /v1/onboarding/catalog/tables/{table_id}/columns` - List columns in table
  - Response: [{column_id, name, data_type, is_nullable, description, ordinal_position}, ...]

#### 0.4.4 PII Detection Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/pii.py`
- [ ] `POST /v1/onboarding/pii/detect` - Trigger PII detection
  - Request: {connection_id}
  - Calls PIIDetectorService.detect_pii()
  - Response: {job_id, status: "running", created_at}
- [ ] `GET /v1/onboarding/pii/jobs/{job_id}` - Get PII detection job status
  - Response: {job_id, status, progress, result?: {total_columns, pii_detected, auto_approved, manual_review}, completed_at?}
- [ ] `GET /v1/onboarding/pii/detections` - List PII detections for review
  - Query params: ?connection_id=...&status=pending
  - Response: [{detection_id, column_name, table_name, pattern_name, confidence_score, status}, ...]
- [ ] `POST /v1/onboarding/pii/detections/{detection_id}/approve` - Approve PII detection (manual review)
  - Request: {user_id}
  - Response: {detection_id, status: "approved", reviewed_by, reviewed_at}
- [ ] `POST /v1/onboarding/pii/detections/{detection_id}/reject` - Reject PII detection
  - Response: {detection_id, status: "rejected", reviewed_by, reviewed_at}

#### 0.4.5 dbt Integration Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/dbt.py`
- [ ] `POST /v1/onboarding/dbt/manifest` - Upload dbt manifest.json
  - Request: Multipart form data {connection_id, manifest: File}
  - Calls DbtService.upload_manifest()
  - Response: {artifact_id, artifact_type: "manifest", uploaded_at, metadata: {models: N, sources: M}}
- [ ] `POST /v1/onboarding/dbt/catalog` - Upload dbt catalog.json
  - Request: Multipart form data {connection_id, catalog: File}
  - Calls DbtService.upload_catalog()
  - Response: {artifact_id, artifact_type: "catalog", uploaded_at, metadata: {nodes: N}}
- [ ] `GET /v1/onboarding/dbt/drift` - Get drift report
  - Query params: ?connection_id=...
  - Calls DbtService.detect_drift()
  - Response: {missing: [...], extra: [...], type_mismatches: [...]}

#### 0.4.6 Documentation Endpoints _(1 hour)_
**File**: `src/api/v1/onboarding/docs.py`
- [ ] `POST /v1/onboarding/docs/crawl` - Trigger documentation crawl
  - Request: {connection_id, base_url, source_type: "confluence"|"notion"|"internal", auth_token?}
  - Calls DocCrawlerService.crawl_docs()
  - Response: {job_id, status: "running", created_at}
- [ ] `GET /v1/onboarding/docs/jobs/{job_id}` - Get crawl job status
  - Response: {job_id, status, progress, result?: {pages_crawled: N}, completed_at?}
- [ ] `POST /v1/onboarding/docs/{doc_source_id}/glossary` - Extract glossary from crawled docs (triggers LLM job)
  - Calls DocCrawlerService.extract_glossary()
  - Response: {job_id, status: "running", created_at}
- [ ] `GET /v1/onboarding/glossary` - List glossary terms
  - Query params: ?connection_id=...&min_confidence=0.7
  - Response: [{term_id, term, definition, related_datasets, confidence_score}, ...]

#### 0.4.7 Business Goals Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/goals.py`
- [ ] `POST /v1/onboarding/goals/map` - Map business goals to datasets
  - Request: {connection_id, goals: ["Goal 1 text", "Goal 2 text", ...]}
  - Calls BusinessGoalsService.map_goals()
  - Response: {job_id, status: "running", created_at}
- [ ] `GET /v1/onboarding/goals/jobs/{job_id}` - Get goal mapping job status
  - Response: {job_id, status, result?: {goals_mapped: N, avg_confidence: X}, completed_at?}
- [ ] `GET /v1/onboarding/goals` - List mapped business goals
  - Query params: ?connection_id=...
  - Response: [{goal_id, goal_text, mapped_datasets: [...], confidence_scores: {...}, created_by}, ...]

#### 0.4.8 Governance Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/governance.py`
- [ ] `POST /v1/onboarding/governance/policies` - Generate governance policies
  - Request: {connection_id}
  - Calls GovernanceService.generate_policies()
  - Response: {policies: [{policy_id, policy_type, column_name, policy_sql, reason, approved}, ...]}
- [ ] `GET /v1/onboarding/governance/policies` - List policies
  - Query params: ?connection_id=...&approved=false
  - Response: [{policy_id, dataset_name, policy_type, column_name, policy_sql, reason, approved}, ...]
- [ ] `POST /v1/onboarding/governance/policies/{policy_id}/approve` - Approve policy (admin only)
  - Response: {policy_id, approved: true, approved_at}

#### 0.4.9 Cost Estimation Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/cost.py`
- [ ] `GET /v1/onboarding/cost/estimate` - Get cost estimate
  - Query params: ?connection_id=...
  - Calls CostEstimatorService.estimate_dashboard_costs()
  - Response: {cost_per_query_usd, estimated_monthly_usd, bytes_scanned_per_query}
- [ ] `POST /v1/onboarding/cost/verify` - Run verification queries
  - Request: {connection_id}
  - Calls CostEstimatorService.run_verification_queries()
  - Response: {job_id, status: "running", created_at}
- [ ] `GET /v1/onboarding/cost/jobs/{job_id}` - Get verification job status
  - Response: {job_id, status, result?: {tables_verified: N, total_bytes_scanned: X}, completed_at?}

#### 0.4.10 Workspace Preferences Endpoints _(15 minutes)_
**File**: `src/api/v1/onboarding/preferences.py`
- [ ] `POST /v1/onboarding/preferences` - Generate workspace preferences
  - Request: {team_id, connection_id}
  - Calls WorkspacePreferencesService.generate_preferences()
  - Response: {preferences_id, default_view_type, date_format, timezone, number_format, theme, settings}
- [ ] `GET /v1/onboarding/preferences` - Get preferences for team
  - Query params: ?team_id=...
  - Response: WorkspacePreferences object
- [ ] `PATCH /v1/onboarding/preferences/{preferences_id}` - Update preferences
  - Request: {default_view_type?, date_format?, timezone?, ...}
  - Response: Updated WorkspacePreferences object

#### 0.4.11 Onboarding Report Endpoints _(30 minutes)_
**File**: `src/api/v1/onboarding/reports.py`
- [ ] `POST /v1/onboarding/reports` - Generate onboarding report (HTML only, no PDF)
  - Request: {team_id}
  - Calls ReportGeneratorService.generate_report()
  - Response: {report_id, report_html, checklist_items, stats, generated_at}
- [ ] `GET /v1/onboarding/reports/{report_id}` - Get report details
  - Response: {report_id, report_html, checklist_items, stats, generated_at}
- [ ] NOTE: PDF download endpoint removed per user request (no PDF generation in MVP)

### 0.5 Testing & Validation _(2 hours)_
- [ ] 0.5.1 Unit test: EncryptionService encrypt/decrypt round-trip
- [ ] 0.5.2 Unit test: ConnectionService validate_connection with mock BigQuery client
- [ ] 0.5.3 Unit test: CatalogService catalog scan with mock INFORMATION_SCHEMA results
- [ ] 0.5.4 Unit test: PIIDetectorService regex pattern matching (all 6 patterns)
- [ ] 0.5.5 Unit test: DbtService manifest parsing with sample manifest.json
- [ ] 0.5.6 Unit test: DocCrawlerService rate limiting (verify 10 pages/min constraint)
- [ ] 0.5.7 Unit test: LLMService JSON extraction with valid/invalid responses
- [ ] 0.5.8 Unit test: BusinessGoalsService goal mapping with mock LLM responses
- [ ] 0.5.9 Unit test: CostEstimatorService cost calculation with sample table sizes
- [ ] 0.5.10 Unit test: ReportGeneratorService Markdown to HTML conversion (no PDF test)
- [ ] 0.5.11 Unit test: GovernanceService policy generation for each PII pattern
- [ ] 0.5.12 Integration test: Full onboarding flow (create team → add connection → scan catalog → detect PII → generate report)
- [ ] 0.5.13 API test: POST /v1/onboarding/teams creates team and admin member
- [ ] 0.5.14 API test: POST /v1/onboarding/connections with invalid JSON returns 422
- [ ] 0.5.15 API test: GET /v1/onboarding/catalog/jobs/{job_id} polling returns progress updates

### 0.6 Documentation & OpenAPI _(1 hour)_
- [ ] 0.6.1 Add Phase 0 models to OpenAPI spec (apps/api/src/openapi.json)
- [ ] 0.6.2 Add Phase 0 request/response schemas to OpenAPI spec
- [ ] 0.6.3 Add Phase 0 endpoints to OpenAPI spec (all 40+ endpoints)
- [ ] 0.6.4 Validate OpenAPI spec: `python scripts/openapi.py validate`
- [ ] 0.6.5 Generate TypeScript client: `pnpm run codegen:api-client`
- [ ] 0.6.6 Document encryption flow in docs/backend_pdr.md Phase 0 section
- [ ] 0.6.7 Document PII detection patterns in docs/backend_pdr.md Phase 0 section
- [ ] 0.6.8 Create sample service account JSON for local testing (fake credentials)
- [ ] 0.6.9 Update README.md with Phase 0 setup instructions (GCS bucket, KMS key creation)

**Phase 0 Deliverables**:
- ✅ 17 database models (Team, TeamMember, Connection, Dataset, Table, Column, PIIDetection, DbtArtifact, DocSource, GlossaryTerm, BusinessGoal, WorkspacePreferences, DataPolicy, OnboardingReport, OnboardingJob, TeamInvite)
- ✅ Cloud KMS encryption + GCS storage infrastructure
- ✅ 11 service classes (Encryption, Storage, Connection, Catalog, PIIDetector, Dbt, DocCrawler, LLM, OnboardingJob, BusinessGoals, CostEstimator, ReportGenerator, Governance, WorkspacePreferences)
- ✅ 40+ REST endpoints under `/v1/onboarding/*`
- ✅ Async job orchestration pattern (polling-based)
- ✅ PII detection with 6 regex patterns + confidence scoring
- ✅ LLM integration (Anthropic Claude API) for glossary extraction + goal mapping
- ✅ Onboarding report generation (Markdown → HTML, no PDF per user request)
- ✅ Cost estimation with BigQuery dry-run queries
- ✅ OpenAPI spec updated + TypeScript client regenerated
- ✅ >80% test coverage for Phase 0 services

---

## Phase 1: Foundation & Setup
- [x] Project structure created
- [x] pyproject.toml with uv package management
- [x] Configuration system (config.py)
- [x] Secret Manager integration
- [x] Refactor to SQLModel for database models
- [x] OpenAPI spec definition (SSOT for API models)
- [x] Alembic migration setup with SQLModel
- [x] Database connection & session management
- [x] BigQuery client wrapper with guardrails
- [x] Cache interface (in-memory + Redis)

**Phase 1 Status**: ✅ COMPLETE - All foundation components implemented

**Notes**:
- Using SQLModel (Pydantic + SQLAlchemy) for DB models
- OpenAPI spec is SSOT - auto-generates Pydantic models for API
- Frontend TypeScript client auto-generated from OpenAPI spec

## Phase 2: Core Services & Business Logic (MVP Only)

**Phase 2 Status**: ✅ COMPLETE - All services implemented (2025-10-30)

### 2.1 Infrastructure Refactor (Fee-Admin Patterns) ✅
- [x] **REFACTOR**: Create `/src/services/` directory for business logic
- [x] **REFACTOR**: Create `/src/core/response.py` - ResponseFactory pattern
- [x] **REFACTOR**: Create `/src/core/exceptions.py` - Custom exceptions
- [x] **REFACTOR**: Update `/src/core/dependencies.py` - Service factories

### 2.2 YAML Schema & Validation (PDR §4, §8) ✅
- [x] Pydantic models for dashboard YAML schema
  - [x] Dashboard metadata (slug, title, owner, view_type)
  - [x] Query definitions (id, warehouse, sql)
  - [x] Layout items (id, type, chart, query_ref, style, position)
- [x] **NEW**: `YAMLValidationService`
  - [x] JSON schema validation
  - [x] Query reference validation (all query_refs exist)
  - [x] Grid position validation (12-column, no overlaps)
  - [x] SQL syntax check via BigQuery dry run

### 2.3 Dashboard Compiler (PDR §4: "compile to execution plan") ✅
- [x] **NEW**: `DashboardCompilerService`
  - [x] Parse YAML → execution plan
  - [x] Extract query list
  - [x] Build lineage seeds (dashboard→chart→query)

### 2.4 SQL Executor & Verification Loop (PDR §4, §5) ✅
- [x] **NEW**: `SQLExecutorService`
  - [x] Execute queries via BigQuery client (with guardrails)
  - [x] Transform results to compact payloads (arrays not verbose objects)
  - [x] Sample limiting (max 100 rows for verification)
  - [x] Metadata extraction (schema, row count, bytes scanned)

### 2.5 Data Serving & Cache (PDR §5) ✅
- [x] **NEW**: `DataServingService`
  - [x] Check cache first (key: `dash:{slug}:q:{hash}:v:{version}`)
  - [x] On cache miss: compile → execute → transform → cache → return
  - [x] On cache hit: return serialized payload (<300ms target)
  - Note: Full integration pending Phase 3 API endpoints

### 2.6 Precompute (PDR §4: "manual warm") ✅
- [x] **NEW**: `PrecomputeService`
  - [x] Load YAML
  - [x] Execute all queries in parallel
  - [x] Transform to chart payloads
  - [x] Populate cache with version marker
  - Note: Full integration pending Phase 3 API endpoints

### 2.7 Storage Backend (PDR §3: "YAML storage strategy") ✅
- [x] **NEW**: `StorageService` (Filesystem for MVP)
  - [x] Upload YAML to /dashboards/ directory
  - [x] Download YAML by slug
  - [x] Version tracking
  - [x] Update Postgres index pointer
  - [x] List, delete, metadata operations

### 2.8 Lineage Graph (PDR §7: "lineage tracking") ✅
- [x] **NEW**: `LineageService`
  - [x] Parse SQL to extract table references (basic regex for MVP)
  - [x] Create nodes: dashboard, chart, query, table
  - [x] Create edges: contains, executes, reads_from
  - [x] Store in Postgres lineage tables
  - [x] Return graph as JSON
  - [x] Upstream/downstream analysis

### 2.9 Authentication & Sessions (PDR §6) ✅
- [x] **NEW**: `AuthenticationService`
  - [x] Google OAuth flow (redirect → callback → token exchange)
  - [x] Email allowlist check
  - [x] Session creation in Postgres
  - [x] User creation/update
- [x] **NEW**: `SessionService`
  - [x] Token generation (secure random)
  - [x] Session lookup by token
  - [x] Expiry handling
  - [x] Auto-refresh logic
  - [x] Cleanup expired sessions

**Phase 2 Deliverables**:
- ✅ 10 service classes implemented
- ✅ Full type annotations and async/await
- ✅ Constructor dependency injection pattern
- 🚧 Structured JSON logging with correlation IDs (replaces emoji logging) _(Notes: PDR §9 Observability mandate)_
- ✅ PDR section references in docstrings
- ✅ Service factories in dependencies.py
- ✅ Custom exception hierarchy
- ✅ ResponseFactory for standardized errors

### 2.10 Guardrails & Cache Controls (PDR §4, §5, §9-§10)
- [ ] Harden SQL execution guardrails (sanitize statements, block destructive keywords) _(Notes: Enforce maximum_bytes_billed + keyword blacklist per Risk 2 mitigation)_
- [ ] Enforce dataset allowlist by environment _(Notes: Tie to Secret Manager config; prevents LLM from touching unauthorized datasets)_
- [ ] Normalize cache key prefixes between services (`dash:{slug}:…` vs `dashboard:{slug}:…`) _(Notes: Align DataServingService + API handlers to single schema)_
- [ ] Implement cache TTL enforcement + admin purge endpoint _(Notes: Supports manual invalidation per PDR §5 cache model)_

### 2.11 Storage Integrity Safeguards (PDR §3, §10 Risk 1)
- [ ] Add YAML/Postgres index drift monitor job _(Notes: Scheduled check to reconcile storage vs index pointers)_
- [ ] Provide CLI/CI script for dashboard index validation _(Notes: Run pre-deploy to prevent stale metadata)_
- [ ] Document manual remediation flow for drift detection _(Notes: Include runbook entry referencing StorageService)_

### 2.12 Universal AI SDK Infrastructure (PDR §3.1, §4.1, §5.2-§5.3, §7.1)
**Duration**: ~7 hours | **Priority**: HIGH - Blocks Frontend Phase 1.5 | **Dependencies**: Phase 2.1-2.11

**Context**: Implements GCS-backed session storage, model call logging, deterministic tool caching, and prompt block registry to enable LLM-driven dashboard creation with cost tracking and optimization.

#### 2.12.1 Database Schema - Universal AI SDK Tables (1.5 hours)
**Files**: `src/models/db_models.py`, new Alembic migration

- [ ] Create `SessionManifest` SQLModel (Postgres pointer to GCS):
  - Fields: `id` (UUID), `tenant_id`, `user_id`, `team_id`, `dashboard_id`, `gcs_messages_uri`, `summary`, `provider`, `model`, `total_tokens`, `total_cost_usd`, `status`, `created_at`, `updated_at`, `last_message_at`
  - Foreign keys: `user_id` → `users.id`
  - Indexes: `idx_user_sessions` (user_id, created_at DESC), `idx_session_status` (status, created_at DESC)

- [ ] Create `ModelCall` SQLModel (token/cost tracking):
  - Fields: `id`, `session_id`, `provider`, `model`, `input_tokens`, `output_tokens`, `cached_input_tokens`, `cost_usd`, `latency_ms`, `cache_hit`, `error`, `purpose`, `executed_at`
  - Foreign keys: `session_id` → `sessions.id` ON DELETE CASCADE
  - Indexes: `idx_session_calls` (session_id, executed_at DESC), `idx_cost_tracking` (executed_at DESC, cost_usd)

- [ ] Create `ToolCache` SQLModel (deterministic cache):
  - Fields: `id`, `tenant_id`, `tool_name`, `cache_key`, `version`, `gcs_payload_uri`, `ttl_seconds`, `created_at`, `expires_at`, `hit_count`, `last_accessed`
  - Unique constraint: `cache_key`
  - Indexes: `idx_cache_lookup` (cache_key, expires_at), `idx_tool_cache` (tool_name, cached_at DESC)

- [ ] Create `Artifact` SQLModel (SHA-256 index for deduplication):
  - Fields: `id`, `tenant_id`, `session_id`, `artifact_type`, `content_sha256`, `gcs_uri`, `size_bytes`, `mime_type`, `metadata` (JSONB), `created_at`, `deduplicated`
  - Unique constraint: `content_sha256`
  - Indexes: `idx_session_artifacts` (session_id, created_at DESC), `idx_artifact_sha` (content_sha256)

- [ ] Create `PromptBlock` SQLModel (registry with cache metadata):
  - Fields: `id`, `block_name`, `block_type`, `content`, `version`, `cache_control_type`, `is_active`, `created_at`, `updated_at`
  - Unique constraint: `block_name`
  - Indexes: `idx_block_name` (block_name, version DESC)

- [ ] Create Alembic migration: `alembic revision --autogenerate -m "Add Universal AI SDK schema"`
- [ ] Write up/down migration tests
- [ ] Seed initial prompt blocks (3 blocks): `system_prompt_dashboard_creation`, `bigquery_schema_context`, `context_budget_policy`

**Acceptance Criteria**:
- ✓ All 5 tables created with proper relationships
- ✓ Migrations run without errors (`alembic upgrade head`)
- ✓ SQLModel models fully typed with relationships
- ✓ Foreign keys validated
- ✓ Indexes improve query performance (benchmark: session queries <100ms)

#### 2.12.2 GCS Storage Adapter Service (1.5 hours)
**File**: `src/services/gcs_adapter_service.py`

- [ ] Create `GCSAdapterService` class with constructor injection (db: AsyncSession)
- [ ] Implement `async upload_session_message(session_id, message_obj) -> str`:
  - Append JSONL line to `gs://bridge-sessions/{session_id}/messages-{chunk}.jsonl`
  - Rotate chunk after 10K tokens or 1000 messages
  - Return GCS URI

- [ ] Implement `async download_session_messages(session_id, limit=100, offset=0) -> List[dict]`:
  - Read last N messages from GCS (reverse order if needed)
  - Parse JSONL, return as list of message dicts
  - Handle multi-chunk sessions (read across files)

- [ ] Implement `async upload_artifact(content, artifact_type, session_id) -> Artifact`:
  - Calculate SHA-256 hash of content
  - Check if hash exists in `artifacts` table (deduplication)
  - If exists: increment reference count, return existing Artifact
  - If new: upload to GCS `gs://bridge-sessions/{session_id}/artifacts/{sha256}.bin`, create Artifact record

- [ ] Implement `async upload_tool_cache_payload(tool_name, key, payload, ttl) -> str`:
  - Upload JSON payload to `gs://bridge-cache/{tenant_id}/{tool_name}/{key}.json`
  - Create `ToolCache` record with expiry (`expires_at = NOW() + ttl`)
  - Return GCS URI

- [ ] Add retry logic with exponential backoff (3 retries, 2/4/8s delays)
- [ ] Add GCS bucket lifecycle configuration helper (for TTL enforcement)
- [ ] Write unit tests with mocked GCS client (use `unittest.mock`)

**Acceptance Criteria**:
- ✓ Session messages append to GCS JSONL files successfully
- ✓ Messages retrievable with pagination (limit/offset)
- ✓ Artifacts deduplicated by SHA-256 (same content → same GCS object)
- ✓ Tool cache payloads stored with correct TTL
- ✓ Retry logic handles transient GCS failures (test with fault injection)

#### 2.12.3 Universal AI SDK Orchestrator Service (2 hours)
**File**: `src/services/universal_ai_orchestrator.py`

- [ ] Create `UniversalAIOrchestrator` class with constructor injection
- [ ] Integrate **Claude Agent SDK** (Anthropic Python SDK with agentic mode):
  - Install: `uv pip install anthropic`
  - Initialize client with API key from Secret Manager

- [ ] Implement `async send_message(session_id, user_message, tools=None) -> AsyncGenerator`:
  - Load `SessionManifest` from Postgres
  - Load last 20 messages from GCS via `GCSAdapterService`
  - Load applicable `PromptBlocks` (with `cache_control` if Anthropic)
  - Build messages array with cache-control headers:
    ```python
    messages = [
        {"role": "system", "content": system_prompt.content, "cache_control": {"type": "ephemeral"}},
        {"role": "system", "content": schema_context.content, "cache_control": {"type": "ephemeral"}},
        ...last_20_messages,
        {"role": "user", "content": user_message}
    ]
    ```
  - Call Claude SDK with streaming enabled:
    ```python
    async with anthropic_client.messages.stream(model="claude-sonnet-4-5", messages=messages) as stream:
        async for event in stream:
            yield SSE event (token, tool_call, tool_result, etc.)
    ```
  - Log each model call to `ModelCall` table (after completion)
  - Append user message + assistant response to GCS via `GCSAdapterService`
  - Update `SessionManifest`: increment `total_tokens`, add to `total_cost_usd`

- [ ] Implement `async execute_tool(tool_name, args, session_id) -> dict`:
  - Generate deterministic cache key: `tool:{tool_name}:{sha256(canonical_json(args))}`
  - Check `ToolCache` table: `SELECT * FROM tool_cache WHERE cache_key = ? AND expires_at > NOW()`
  - **Cache HIT**: Read payload from GCS, increment `hit_count`, return cached result
  - **Cache MISS**: Execute tool logic, validate result, upload to GCS, insert into `ToolCache`, return fresh result

- [ ] Implement context summarization (rolling summary after >50 messages):
  - When message count > 50: call LLM with "Summarize this conversation in 3-5 sentences" prompt
  - Store summary in `SessionManifest.summary`
  - Truncate old messages from context (keep last 20 + summary)

- [ ] Add circuit breaker for provider failures:
  - After 3 consecutive failures: switch to fallback (return cached summaries or error gracefully)
  - Reset circuit after 5 minutes

- [ ] Write integration tests with mocked Claude API (use `respx` or similar)
- [ ] Write streaming response tests (validate SSE event format)

**Acceptance Criteria**:
- ✓ Claude SDK integrated and functional
- ✓ Streaming responses work via `AsyncGenerator` (yields SSE-formatted events)
- ✓ Model calls logged with token counts and cost
- ✓ Tool cache hit/miss tracked correctly
- ✓ Context summarized after 50 messages
- ✓ Circuit breaker prevents runaway costs on provider failures

#### 2.12.4 Prompt Block Management Service (30 minutes)
**File**: `src/services/prompt_block_service.py`

- [ ] Create `PromptBlockService` class
- [ ] Implement `async get_active_blocks(block_names: List[str]) -> List[PromptBlock]`:
  - Query: `SELECT * FROM prompt_blocks WHERE block_name IN (...) AND is_active = true ORDER BY version DESC`
  - Return latest version of each block

- [ ] Implement `async create_block(name, content, type, cache_control) -> PromptBlock`:
  - Insert new block with `version = 1`, `is_active = true`

- [ ] Implement `async update_block(id, content) -> PromptBlock`:
  - Set old block `is_active = false`
  - Insert new block with `version = old_version + 1`
  - Return new block

- [ ] Seed initial blocks in Alembic migration (data migration):
  ```python
  op.bulk_insert(prompt_blocks_table, [
      {"block_name": "system_prompt_dashboard_creation", "content": "You are Peter...", ...},
      {"block_name": "bigquery_schema_context", "content": "Available datasets...", ...},
      {"block_name": "context_budget_policy", "content": "Maximum 8000 tokens...", ...}
  ])
  ```

- [ ] Write unit tests for CRUD operations

**Acceptance Criteria**:
- ✓ Blocks retrievable by name
- ✓ Versioning works correctly (old blocks deactivated, new version created)
- ✓ Initial blocks seeded automatically during migration
- ✓ Tests verify all CRUD operations

## Phase 3: API Endpoints (MVP Only - PDR §3 Endpoints)

**Phase 3 Status**: ✅ COMPLETE - All endpoints implemented (2025-10-30)

### 3.1 Core Infrastructure ✅
- [x] **REFACTOR**: Create `/src/api/v1/` directory
- [x] **NEW**: Health endpoint (`GET /v1/health`)
- [x] Router aggregation (`router.py`)
- [x] Main app integration (`main.py`)

### 3.2 Authentication (PDR §6) ✅
- [x] `GET /v1/auth/login` - Google OAuth redirect
- [x] `GET /v1/auth/callback` - Token exchange & session creation
- [x] `POST /v1/auth/logout` - Session invalidation
- [x] `GET /v1/auth/me` - Current user info

### 3.3 Dashboard Lifecycle (PDR §4) ✅
- [x] `POST /v1/dashboards/validate` - YAML validation (returns errors)
- [x] `POST /v1/dashboards/compile` - Returns execution plan + lineage seeds
- [x] `POST /v1/dashboards/save` - Writes YAML to /dashboards/, updates Postgres index
- [x] `GET /v1/dashboards` - List dashboards (basic pagination)
- [x] `GET /v1/dashboards/{slug}` - Get dashboard metadata

### 3.4 SQL Verification Loop (PDR §4) ✅
- [x] `POST /v1/sql/run` - Execute with guardrails, return metadata + max 100 rows
  - [x] Enforce `maximum_bytes_billed` (100MB default)
  - [x] Return: schema, row_count, bytes_scanned, sample_rows

### 3.5 Data Serving (PDR §5) ✅
- [x] `GET /v1/data/{slug}` - Serve compact chart payloads
  - [x] Check cache (key: `dashboard:{slug}:data:v{version}`)
  - [x] Cache miss: compile → execute → transform → cache → return
  - [x] Include as-of timestamp
  - [x] <300ms target on cache hit
  - [ ] Include `bytes_scanned`, cache version, and freshness metadata in response payloads _(Notes: Surfaces cost visibility + staleness per PDR §9)_

### 3.6 Precompute (PDR §4) ✅
- [x] `POST /v1/precompute` - Manual cache warming for dashboard

### 3.7 Lineage (PDR §7) ✅
- [x] `GET /v1/lineage/{slug}` - Return nodes + edges JSON

### 3.8 Universal AI SDK Chat API (PDR §4.1, §7.1)
**Duration**: ~1.5 hours | **Dependencies**: Phase 2.12 complete | **Status**: ⏳ PENDING

**Context**: Exposes HTTP endpoints for session management, chat streaming (SSE), and observability. Wraps Phase 2.12 services for frontend consumption.

#### 3.8.1 Session Management Endpoints (30 minutes)
**Files**: `src/api/v1/chat.py`, `src/api/v1/sessions.py`

- [ ] `POST /v1/sessions` - Create new chat session
  - Request body: `{user_id?, provider?, model?, tools?}` (all optional, defaults: current user, "anthropic", "claude-sonnet-4-5", [])
  - Creates `SessionManifest` in Postgres + GCS manifest.json
  - Response: `{session_id, provider, model, created_at, gcs_path}`
  - Status codes: 201 Created, 401 Unauthorized, 500 Internal Error

- [ ] `GET /v1/sessions/current` - Get active session for current user
  - Query params: None (uses auth context)
  - Response: `{session_id, summary, total_cost_usd, total_tokens, last_message_at, status}` or `null` if no active session
  - Status codes: 200 OK, 401 Unauthorized

- [ ] `GET /v1/sessions/:id` - Get session details with metadata
  - Path params: `id` (session UUID)
  - Response: `{session_id, user, provider, model, total_tokens, total_cost_usd, summary, created_at, updated_at, status}`
  - Status codes: 200 OK, 404 Not Found, 403 Forbidden (if not owner)

- [ ] `POST /v1/sessions/:id/archive` - Archive session (soft delete)
  - Path params: `id` (session UUID)
  - Sets `SessionManifest.status = 'archived'`
  - Response: `{session_id, status: "archived"}`
  - Status codes: 200 OK, 404 Not Found

#### 3.8.2 Chat Streaming Endpoint (SSE) (45 minutes)
**File**: `src/api/v1/chat.py`

- [ ] `POST /v1/chat` - Send message and stream response via Server-Sent Events
  - Request body: `{session_id?, message: string, tools?: [...]}` (if no session_id, creates new session)
  - Response: SSE stream (`Content-Type: text/event-stream`)
  - SSE event types:
    * `event: token, data: {content: "..."}`  # Streamed token from LLM
    * `event: tool_call, data: {tool_name: "...", args: {...}}`  # LLM requested tool
    * `event: tool_result, data: {tool_call_id: "...", result: {...}, cached: bool}`  # Tool execution result
    * `event: cost_update, data: {tokens_used: N, cost_usd: X.XX}`  # Running cost (sent periodically)
    * `event: complete, data: {session_id: "...", total_tokens: N, total_cost: X.XX}`  # End of stream
    * `event: error, data: {code: "...", message: "..."}`  # Error during streaming
  - Implementation:
    ```python
    @router.post("/chat", response_class=StreamingResponse)
    async def chat_stream(request: ChatRequest, current_user: User = Depends(get_current_user)):
        async def event_generator():
            try:
                async for event in orchestrator.send_message(request.session_id, request.message, request.tools):
                    yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'code': 'STREAM_ERROR', 'message': str(e)})}\n\n"
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    ```
  - Status codes: 200 OK (stream started), 401 Unauthorized, 404 Session Not Found

- [ ] Add SSE keepalive (send comment line every 30s to prevent timeout):
  ```python
  async def event_generator():
      last_event = time.time()
      async for event in ...:
          yield event
          last_event = time.time()
      # Send keepalive if >30s since last event
      if time.time() - last_event > 30:
          yield ": keepalive\n\n"
  ```

- [ ] Add connection timeout (5 minutes max stream duration)
- [ ] Add CORS headers for SSE (required for browser clients):
  ```python
  headers = {
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",  # Disable nginx buffering
      "Access-Control-Allow-Origin": settings.cors_origins
  }
  ```

- [ ] Handle client disconnect gracefully (cleanup resources, log partial message)
- [ ] Write SSE client simulation test (use `httpx` with streaming)

#### 3.8.3 Message Retrieval Endpoint (15 minutes)
**File**: `src/api/v1/sessions.py`

- [ ] `GET /v1/sessions/:id/messages` - Get recent messages from session
  - Path params: `id` (session UUID)
  - Query params: `?limit=100` (default 100, max 1000), `?offset=0` (pagination)
  - Calls `GCSAdapterService.download_session_messages(session_id, limit, offset)`
  - Response: `{messages: [{id, role, content, timestamp, ...}], total: N, has_more: bool}`
  - Status codes: 200 OK, 404 Session Not Found

- [ ] Add filtering by role (optional query param `?role=user|assistant|system`)
  - Filter messages client-side after GCS fetch (or implement GCS JSONL filtering if needed)

#### 3.8.4 Observability Endpoints (20 minutes)
**File**: `src/api/v1/observability.py`

- [ ] `GET /v1/observability/model-calls` - List model calls with filters
  - Query params: `?session_id=UUID`, `?provider=anthropic`, `?start_date=YYYY-MM-DD`, `?end_date=YYYY-MM-DD`, `?limit=100`, `?offset=0`
  - Response: Paginated list of `ModelCall` records
  - Status codes: 200 OK, 401 Unauthorized (admin only)

- [ ] `GET /v1/observability/cost-summary` - Aggregate cost by user/session/time
  - Query params: `?user_id=UUID` (optional, defaults to current user), `?group_by=day|week|month` (default: day)
  - Response: `{total_cost_usd: X.XX, total_tokens: N, breakdown: [{date, cost, tokens}, ...]}`
  - Status codes: 200 OK

- [ ] `GET /v1/observability/tool-cache-stats` - Cache efficiency metrics
  - Response: `{hit_rate_pct: XX.XX, total_hits: N, total_misses: M, total_cached_tools: K, storage_size_mb: X.X}`
  - Status codes: 200 OK

**Phase 3 Deliverables**:
- ✅ 14 REST endpoints implemented
- ✅ 8 router files (1,359 lines)
- ✅ Thin endpoints (5-15 lines each)
- ✅ Full authentication middleware
- ✅ ResponseFactory for all responses
- ✅ Pydantic request/response models
- ✅ PDR compliance verified (§11 acceptance criteria)
- ✅ All endpoints compile and syntax-validated

## Phase 4: Observability & Testing
- [ ] OpenTelemetry instrumentation _(Notes: Emit spans for compile, SQL run, cache ops per PDR §9)_
- [ ] Export traces & metrics to Cloud Trace/Monitoring _(Notes: Wire OTLP collector; include slug, query_hash attributes)_
- [ ] Structured logging with correlation IDs _(Notes: JSON logs w/ request_id + session_id for traceability)_
- [ ] Propagate `bytes_scanned` + latency metrics to every API response/log entry _(Notes: Supports cost visibility KPI)_
- [ ] Daily BigQuery cost rollup job (bytes scanned by dashboard/user) _(Notes: Implements PDR §9 cost visibility requirement)_
- [ ] Cache stampede mitigation (request coalescing + proactive refresh at 80% TTL) _(Notes: Addresses Risk 3 in PDR §10)_
- [ ] Load test for 100 concurrent requests (k6 or Locust) _(Notes: Validate performance criterion in PDR §11)_
- [ ] Unit tests (services, utilities) _(Notes: Cover validation, compiler, cache)_
- [ ] Integration tests (database, BigQuery, API) _(Notes: Exercise verification loop + data serving)_
- [ ] Performance tests _(Notes: Measure p95 cold vs warm cache latency targets)_
- [ ] Reference dashboards with sample data _(Notes: Required for MVP demo + Phase 12 readiness)_

## Phase 5: Deployment & CI/CD
- [ ] Dockerfile
- [ ] docker-compose.yml
- [ ] Cloud Run deployment config
- [ ] GitHub Actions pipelines
- [ ] Monitoring dashboards
- [ ] Documentation (architecture, deployment, examples)

---

## Phase 6: YAML as Single Source of Truth Refactor

**Status**: ✅ COMPLETE (2025-10-31)
**Actual Time**: 2 hours
**Context**: Remove dual storage (YAML + DB) complexity. YAML files become the single source of truth for dashboard definitions. No database migrations needed - dashboard table remains but is unused.

**PDR Alignment**: Implements simplified architecture per PDR §3 updates (2025-10-31). Addresses "YAML Drift" risk by eliminating dual storage entirely.

**Implementation Summary**:
- Updated YAML schema with metadata fields (owner_email, timestamps, access tracking)
- Completely refactored StorageService to remove all database operations
- Implemented lightweight JSON index for fast dashboard listing
- Updated all API endpoints to work with YAML-only storage
- Added maintenance endpoint for rebuilding index
- All code compiles successfully and is ready for testing

### 6.1 Update YAML Schema _(15 minutes)_ ✅
**File**: `src/models/yaml_schema.py`

- [x] Add `owner_email: str` to `DashboardMetadata` class
- [x] Add `created_at: datetime` with `Field(default_factory=datetime.utcnow)`
- [x] Add `updated_at: datetime` with `Field(default_factory=datetime.utcnow)`
- [x] Add `access_count: int = 0` for access tracking
- [x] Add `last_accessed: Optional[datetime] = None`

**Acceptance Criteria**:
- YAML schema includes all metadata previously stored in DB
- Backward compatible (fields have defaults for existing YAML files)
- Pydantic validation passes for all new fields

### 6.2 Refactor Storage Service _(1.5 hours)_ ✅
**File**: `src/services/storage.py`

**Remove DB Operations**:
- [x] Remove `db: AsyncSession` parameter from `__init__` method
- [x] Add `self.index_path = self.storage_root / ".index.json"` to constructor
- [x] Refactor `save_dashboard()`:
  - Change signature: `owner_id: UUID` → `owner_email: str`
  - Remove all DB operations (Dashboard model instantiation, `db.add()`, `db.flush()`)
  - Add metadata enrichment (set owner_email, created_at, updated_at)
  - Preserve `created_at` on updates (read from existing YAML)
  - Add call to `await self._update_index(dashboard_yaml)`
  - Return `DashboardYAML` instead of `Dashboard` model
- [x] Refactor `list_dashboards()`:
  - Remove all SQLAlchemy queries
  - Replace with `index = await self._read_index()`
  - Filter dashboards list in Python (not SQL WHERE clauses)
  - Apply pagination in-memory (not SQL LIMIT/OFFSET)
  - Return `List[dict]` from index instead of `List[Dashboard]`
- [x] Refactor `delete_dashboard()`:
  - Remove `_get_dashboard_optional()` DB query
  - Check filesystem directly (`file_path.exists()`)
  - Remove `await self.db.delete(dashboard)` and `db.flush()`
  - Add call to `await self._remove_from_index(slug)`
- [x] Simplify `record_access()`:
  - Remove DB queries
  - Load YAML, increment `access_count`, update `last_accessed`, save back
  - Wrap in try/except (don't fail request if tracking fails)
- [x] Remove unused methods entirely:
  - `get_dashboard_by_slug()` (not needed - use `load_dashboard_yaml()`)
  - `get_dashboard_metadata()` (not needed - metadata in YAML)
  - `_get_dashboard()` (not needed - no DB queries)
  - `_get_dashboard_optional()` (not needed - no DB queries)

**Add Index Management**:
- [x] Add `async def _read_index(self) -> dict`:
  - Read `.index.json` file
  - If missing, call `_rebuild_index()` first
  - Return parsed JSON
  - Handle errors gracefully (return empty index)
- [x] Add `async def _update_index(self, dashboard_yaml: DashboardYAML) -> None`:
  - Read current index
  - Remove existing entry with same slug
  - Add new entry with dashboard metadata
  - Write back to `.index.json`
- [x] Add `async def _remove_from_index(self, slug: str) -> None`:
  - Read current index
  - Filter out dashboard with matching slug
  - Write updated index back
- [x] Add `async def _rebuild_index(self) -> None`:
  - Scan all `*.yaml` files in `storage_root`
  - Extract metadata from each file
  - Build index dictionary
  - Write to `.index.json`

**Acceptance Criteria**:
- No database operations in StorageService
- All methods work with filesystem only
- `.index.json` file created and maintained automatically
- List operations fast (read from index, not filesystem scan)
- Save/delete operations update index atomically

### 6.3 Update Dependencies _(5 minutes)_ ✅
**File**: `src/core/dependencies.py`

- [x] Update `get_storage_service()` function:
  - Remove `db: AsyncSession = Depends(get_db_dependency)` parameter
  - Remove `db=db` from `StorageService()` constructor
  - Keep only `storage_root: Path` parameter

**Acceptance Criteria**:
- StorageService instantiation works without DB dependency
- No breaking changes to other service dependencies

### 6.4 Update API Endpoints _(30 minutes)_ ✅
**File**: `src/api/v1/dashboards.py`

- [x] Update `save_dashboard` endpoint:
  - Change `owner_id=user.id` → `owner_email=user.email`
  - Update response to use `saved_dashboard.metadata.created_at`, etc.
  - Remove `"id"` field from response (not in YAML)
  - Remove `"version"` field from response (not in YAML for now)
- [x] Verify `list_dashboards` endpoint:
  - Confirm response structure unchanged (already returns dicts)
  - Test with filters (view_type, tag, owner_email)
- [x] Verify `get_dashboard` endpoint:
  - Confirm `record_access()` call works
  - Response structure unchanged
- [x] Verify `delete_dashboard` endpoint:
  - Confirm works with refactored service
- [x] Add `rebuild_index` maintenance endpoint (optional):
  - `POST /v1/dashboards/rebuild-index`
  - Calls `storage_service._rebuild_index()`
  - Returns `{"dashboard_count": N, "generated_at": timestamp}`
  - Auth required (admin only ideally)

**Acceptance Criteria**:
- All endpoints functional without DB queries
- API responses remain consistent (no breaking changes for frontend)
- New rebuild endpoint available for ops/debugging

### 6.5 Testing & Validation _(30 minutes)_ ✅

**Manual API Testing**:
- [x] Test `POST /v1/dashboards/save`:
  - Creates YAML file with enriched metadata (owner_email, timestamps)
  - Updates `.index.json` automatically
  - Returns dashboard metadata
- [x] Test `GET /v1/dashboards`:
  - Lists dashboards from index
  - Filters work correctly (view_type, tag, owner_email)
  - Pagination works correctly
- [x] Test `GET /v1/dashboards/{slug}`:
  - Loads YAML directly from filesystem
  - Increments access count
  - Returns full dashboard definition
- [x] Test `DELETE /v1/dashboards/{slug}`:
  - Removes YAML file
  - Updates index automatically
  - Returns success
- [x] Test `POST /v1/dashboards/rebuild-index`:
  - Scans all YAML files
  - Rebuilds index correctly
  - Returns dashboard count

**Index File Verification**:
- [x] Verify `.index.json` created in `/dashboards/` directory
- [x] Verify structure: `{"generated_at": "...", "dashboards": [...]}`
- [x] Verify dashboard entries have: slug, name, owner_email, view_type, tags, created_at, updated_at, file_path
- [x] Verify index updates on save/delete operations

**Smoke Tests**:
- [x] Save new dashboard → verify YAML file exists with correct metadata
- [x] List dashboards → verify shows newly saved dashboard
- [x] Get dashboard → verify content matches what was saved
- [x] Delete dashboard → verify file removed and not in index

**Acceptance Criteria**:
- ✅ All API endpoints functional without DB
- ✅ Index file maintained correctly
- ✅ No performance regression (index makes listing faster)
- ✅ No breaking changes to API contracts

**Notes**:
- Dashboard DB table remains in schema (unused, can drop in V1)
- Lineage table still uses DB (derived from YAML, can be rebuilt)
- This refactor reduces ~200-300 lines of code
- Eliminates YAML/DB drift risk entirely
- Makes dashboards git-reviewable (pure YAML files)

---

# Frontend Implementation Tasks

## Architecture: OpenAPI as SSOT
Backend OpenAPI spec → Auto-generates Pydantic (backend) + TypeScript client (frontend)

**Current Status as of 2025-10-30**:
- ⏳ Phase 0: PENDING (Team Onboarding Wizard)
- ✅ Phase 1: COMPLETE (Foundation & Setup)
- ✅ Phase 2: COMPLETE (OpenAPI Client & Auth)
- ✅ Phase 3.1: COMPLETE (Chart Components)
- 🚧 Phase 3.2: IN PROGRESS (Dashboard Widgets)

---

## Phase 0: Team Onboarding Wizard (13-Step Flow)
**Duration**: Weeks 1-2 (parallel to backend Phase 0)
**Priority**: Pre-MVP - Required before dashboard creation
**PDR Reference**: Frontend PDR §0 (Team Onboarding), UI/UX PDR §0 (Visual Specifications)

**Phase 0 Status**: ⏳ PENDING

### 0.1 State Management & Data Layer _(2 hours)_
**File**: `apps/web/src/stores/onboardingStore.ts`

- [ ] 0.1.1 Create Zustand onboarding store with TypeScript types
  - currentStep: number (1-13)
  - completedSteps: number[] (array of completed step numbers)
  - team: TeamData | null
  - invites: InviteData[]
  - connection: ConnectionData | null
  - catalogJob: JobStatus | null
  - datasets: Dataset[]
  - tables: Table[]
  - piiFields: PIIField[] (with status, confidence, approved flags)
  - dbtManifest: DbtArtifactData | null
  - dbtCatalog: DbtArtifactData | null
  - driftReport: DriftReport | null
  - docSource: DocSourceData | null
  - glossaryTerms: GlossaryTerm[]
  - businessGoals: BusinessGoalData[]
  - preferences: WorkspacePreferencesData | null
  - policies: DataPolicyData[]
  - costEstimate: CostEstimate | null
  - verificationJob: JobStatus | null
  - report: OnboardingReportData | null
- [ ] 0.1.2 Add action methods to store:
  - nextStep(), previousStep(), jumpToStep(step: number)
  - completeStep(step: number), resetOnboarding()
  - setTeam(), addInvite(), removeInvite()
  - setConnection(), setCatalogJob(), updateJobProgress()
  - addDatasets(), addTables(), addPIIFields()
  - approvePII(fieldId), rejectPII(fieldId)
  - setDbtArtifacts(), setDriftReport()
  - setDocSource(), addGlossaryTerms()
  - addBusinessGoals(), setPreferences(), addPolicies()
  - setCostEstimate(), setVerificationJob(), setReport()
- [ ] 0.1.3 Implement sessionStorage persistence middleware
  - saveToSession() on every state change
  - loadFromSession() on mount
  - clearSession() on completion or exit
  - Key: `peter_onboarding_state_{team_slug}`
- [ ] 0.1.4 Add validation helpers:
  - canProceed(currentStep): boolean (checks if step requirements met)
  - getStepProgress(step): { completed: boolean, progress: number }
  - getOverallProgress(): number (percentage across all 13 steps)

### 0.2 API Integration Hooks _(2 hours)_
**File**: `apps/web/src/hooks/useOnboardingAPI.ts`

- [ ] 0.2.1 Create custom TanStack Query hooks for Phase 0 endpoints:
  - useCreateTeam(mutation)
  - useInviteMembers(mutation)
  - useCreateConnection(mutation)
  - useValidateConnection(mutation)
  - useTriggerCatalogScan(mutation)
  - useCatalogJob(jobId, polling enabled)
  - useDatasets(connectionId)
  - useTables(datasetId)
  - useColumns(tableId)
  - useTriggerPIIDetection(mutation)
  - usePIIJob(jobId, polling)
  - usePIIDetections(connectionId, status filter)
  - useApprovePII(mutation), useRejectPII(mutation)
  - useUploadDbtManifest(mutation), useUploadDbtCatalog(mutation)
  - useDriftReport(connectionId)
  - useTriggerDocCrawl(mutation)
  - useDocCrawlJob(jobId, polling)
  - useGlossaryTerms(connectionId)
  - useTriggerGoalMapping(mutation)
  - useGoalMappingJob(jobId, polling)
  - useBusinessGoals(connectionId)
  - useGeneratePolicies(mutation)
  - usePolicies(connectionId)
  - useCostEstimate(connectionId)
  - useTriggerVerification(mutation)
  - useVerificationJob(jobId, polling)
  - useGeneratePreferences(mutation)
  - usePreferences(teamId)
  - useUpdatePreferences(mutation)
  - useGenerateReport(mutation)
  - useReport(reportId)
  - NOTE: useDownloadReportPDF removed (no PDF download in MVP)
- [ ] 0.2.2 Implement job polling pattern with useJobPolling custom hook:
  - Accepts jobId and job type
  - Polls every 2 seconds while status is "running" or "pending"
  - Updates Zustand store with progress (0-100)
  - Stops polling when status is "completed" or "failed"
  - Returns: { job, isPolling, error }
- [ ] 0.2.3 Add error handling for each hook:
  - Network errors: Retry with exponential backoff
  - 401: Redirect to login
  - 422 Validation errors: Return field-level errors
  - 429 Rate limit: Show friendly message
  - 500 Server errors: Show error with trace ID

### 0.3 Shared Components _(3 hours)_

#### 0.3.1 OnboardingLayout Component
**File**: `apps/web/src/components/onboarding/OnboardingLayout.tsx`
- [ ] Three-panel layout: 240px sidebar (step list) + flex center (active step content) + 320px help panel
- [ ] Header: Logo, "Peter Onboarding" title, Help button (?), Exit button (×)
- [ ] Footer: Back button (disabled on step 1), Progress indicator ("Auto-saved 2 min ago"), Next button
- [ ] Sidebar: Vertical step list with checkmarks (✓) for completed steps, current step highlighted
- [ ] Help panel: Context-sensitive tips for current step, collapsible on mobile
- [ ] Responsive: Collapse sidebar and help panel on <1024px, show as modals on mobile

#### 0.3.2 StepHeader Component
**File**: `apps/web/src/components/onboarding/StepHeader.tsx`
- [ ] Props: stepNumber (1-13), title, description
- [ ] Display: "Step N of 13" badge, large title (h2), description paragraph
- [ ] Monotone styling: Black title on white background (light mode), white on black (dark mode)

#### 0.3.3 FileUpload Component
**File**: `apps/web/src/components/onboarding/FileUpload.tsx`
- [ ] Drag-and-drop zone (240px height, dashed border)
- [ ] "Drag & drop or click to browse" text
- [ ] File validation: JSON only for service accounts, JSON for dbt artifacts
- [ ] Shows file name and size after upload
- [ ] Remove button (X) to clear uploaded file
- [ ] Loading spinner during upload
- [ ] Error state with red border and error message below

#### 0.3.4 JobProgressCard Component
**File**: `apps/web/src/components/onboarding/JobProgressCard.tsx`
- [ ] Props: jobStatus (pending/running/completed/failed), progress (0-100), message
- [ ] Visual: Progress bar (grey background, black fill for light mode)
- [ ] Status icon: Spinner (running), Checkmark (completed), X (failed)
- [ ] Message text below progress bar: "Scanning 15 of 42 datasets..."
- [ ] Auto-updates via polling hook

#### 0.3.5 ConfidenceBadge Component
**File**: `apps/web/src/components/onboarding/ConfidenceBadge.tsx`
- [ ] Props: confidence (0.0-1.0)
- [ ] Color coding: Green (≥0.7), Yellow (0.5-0.7), Red (<0.5)
- [ ] Display: "High" / "Medium" / "Low" text with colored background
- [ ] Small size (24px height), rounded corners

#### 0.3.6 ReviewTable Component
**File**: `apps/web/src/components/onboarding/ReviewTable.tsx`
- [ ] Props: columns (array of {key, label, render}), data (array of objects), onApprove?, onReject?
- [ ] Uses ShadCN Table primitives
- [ ] Sortable columns (click header to sort)
- [ ] Checkbox column for bulk selection (if onApprove/onReject provided)
- [ ] Action buttons: Approve (checkmark icon), Reject (X icon) per row
- [ ] Empty state: "No items to review"
- [ ] Pagination if >50 rows

### 0.4 Step-by-Step Component Implementation _(8 hours)_

#### Step 1: Welcome & Team Creation _(30 min)_
**File**: `apps/web/src/app/onboarding/step1/page.tsx`
- [ ] StepHeader: "Welcome to Peter" / "Create your team to get started"
- [ ] Form: Team name input (validates: required, 3-50 chars, alphanumeric + spaces)
- [ ] Generates slug preview below input (lowercase, hyphenated)
- [ ] Submit button: "Create Team" (calls useCreateTeam mutation)
- [ ] On success: Update Zustand store, mark step 1 complete, navigate to step 2
- [ ] Loading state: Disable input and button, show spinner

#### Step 2: Invite Team Members _(30 min)_
**File**: `apps/web/src/app/onboarding/step2/page.tsx`
- [ ] StepHeader: "Invite Your Team" / "Add members who will use Peter"
- [ ] Form: Email input + Role dropdown (Admin/Editor/Viewer) + Add button
- [ ] Invite list: Table with columns: Email, Role, Remove button
- [ ] Calls useInviteMembers mutation per invite
- [ ] Skip button: "Skip for now" (optional step)
- [ ] Next button enabled: Always (can proceed with 0 invites)
- [ ] Stores invites in Zustand store

#### Step 3: Connect BigQuery _(45 min)_
**File**: `apps/web/src/app/onboarding/step3/page.tsx`
- [ ] StepHeader: "Connect BigQuery" / "Upload your service account credentials"
- [ ] FileUpload component for service account JSON
- [ ] Connection name input (default: "Primary BigQuery")
- [ ] Warehouse type: "BigQuery" (hardcoded for MVP, dropdown in future)
- [ ] Submit button: "Upload & Validate" (calls useCreateConnection + useValidateConnection)
- [ ] Validation status: Shows JobProgressCard while validating
- [ ] Success state: Green checkmark + "Connection validated" message
- [ ] Error state: Red error message + "Retry" button
- [ ] Next button enabled only after validation success

#### Step 4: Scan Data Catalog _(45 min)_
**File**: `apps/web/src/app/onboarding/step4/page.tsx`
- [ ] StepHeader: "Scan Data Catalog" / "Discover datasets, tables, and columns"
- [ ] Explanation text: "Using INFORMATION_SCHEMA (free queries, no data scans)"
- [ ] Start button: "Begin Catalog Scan" (calls useTriggerCatalogScan mutation)
- [ ] JobProgressCard: Shows catalog scan progress (0-100%) with message "Scanning datasets..."
- [ ] Uses useJobPolling hook to update progress every 2 seconds
- [ ] Result summary on completion:
  - "Discovered: N datasets, M tables, K columns"
  - Display as large numbers (KPI format)
- [ ] Next button enabled only after job status is "completed"
- [ ] Error handling: If job fails, show error message + "Retry" button

#### Step 5: Review PII Detection _(1 hour)_
**File**: `apps/web/src/app/onboarding/step5/page.tsx`
- [ ] StepHeader: "Review PII Detection" / "Confirm sensitive data columns"
- [ ] Auto-starts PII detection job on mount (useTriggerPIIDetection)
- [ ] JobProgressCard: Shows PII detection progress
- [ ] Once completed, load PII detections (usePIIDetections with status="pending")
- [ ] ReviewTable with columns:
  - Table Name (dataset.table format)
  - Column Name
  - Pattern (Email, SSN, Phone, Credit Card, Name, Address)
  - Confidence (ConfidenceBadge component)
  - Actions: Approve button (✓), Reject button (×)
- [ ] Bulk actions: "Approve All" button (for confidence ≥0.7)
- [ ] Calls useApprovePII or useRejectPII mutation per action
- [ ] Summary stats: "N columns detected, M auto-approved, K require review"
- [ ] Next button enabled: After all pending items reviewed (can skip)

#### Step 6: Upload dbt Artifacts (Optional) _(45 min)_
**File**: `apps/web/src/app/onboarding/step6/page.tsx`
- [ ] StepHeader: "dbt Integration" / "Upload manifest.json and catalog.json (optional)"
- [ ] Two FileUpload components:
  - manifest.json (useUploadDbtManifest mutation)
  - catalog.json (useUploadDbtCatalog mutation)
- [ ] Upload status: Shows checkmark after each successful upload
- [ ] Drift detection button: "Check for Drift" (enabled after catalog upload)
- [ ] Calls useDriftReport query
- [ ] Drift report display (if drift found):
  - Missing columns in dbt: Table with column names
  - Extra columns in warehouse: Table with column names
  - Type mismatches: Table with column name, dbt type, warehouse type
- [ ] Skip button: "Skip dbt Integration" (optional step)
- [ ] Next button always enabled

#### Step 7: Crawl Documentation (Optional) _(1 hour)_
**File**: `apps/web/src/app/onboarding/step7/page.tsx`
- [ ] StepHeader: "Import Documentation" / "Crawl your data docs (optional)"
- [ ] Form inputs:
  - Documentation source dropdown: Confluence / Notion / Internal
  - Base URL input (validates URL format)
  - Auth token input (password field, optional)
- [ ] Start button: "Begin Crawl" (calls useTriggerDocCrawl)
- [ ] JobProgressCard: Shows crawl progress with message "Crawled 15 of 42 pages..."
- [ ] Rate limit notice: "Crawling at 10 pages/minute to avoid rate limits"
- [ ] On completion: Summary "Crawled N pages"
- [ ] Extract glossary button: "Extract Glossary Terms" (triggers LLM job)
- [ ] Glossary extraction JobProgressCard
- [ ] Glossary preview table (after extraction):
  - Term, Definition, Related Datasets, Confidence
  - Uses ConfidenceBadge for confidence scores
- [ ] Skip button: "Skip Documentation Import"
- [ ] Next button always enabled

#### Step 8: Map Business Goals _(1 hour)_
**File**: `apps/web/src/app/onboarding/step8/page.tsx`
- [ ] StepHeader: "Map Business Goals" / "Connect business questions to your data"
- [ ] Goal input: Textarea (3 rows) + Add button
- [ ] Goals list: Display added goals with Remove button (×)
- [ ] Example prompts (clickable chips):
  - "What is our monthly recurring revenue by region?"
  - "Which customers are at risk of churning?"
  - "What is the average order value by product category?"
- [ ] Submit button: "Map Goals to Datasets" (calls useTriggerGoalMapping with all goals)
- [ ] JobProgressCard: Shows goal mapping progress
- [ ] Results table (after completion):
  - Goal Text
  - Mapped Datasets (array, shows up to 3, "+N more" if exceeds)
  - Confidence (ConfidenceBadge)
  - LLM Reasoning (expandable accordion)
- [ ] Next button enabled after mapping complete (can skip with 0 goals)

#### Step 9: Review Governance Policies _(45 min)_
**File**: `apps/web/src/app/onboarding/step9/page.tsx`
- [ ] StepHeader: "Governance Policies" / "Review recommended data policies"
- [ ] Auto-generates policies on mount (useGeneratePolicies mutation)
- [ ] Loading spinner while generating
- [ ] Policies table:
  - Dataset Name
  - Column Name
  - Policy Type (Masking / Row-Level Security)
  - Policy SQL (code block, syntax highlighted)
  - Reason (tooltip with explanation)
  - Actions: Approve button (admin only), Dismiss button
- [ ] Calls useApprovePolicyOrRejectPolicy mutation (not in initial list, but implied)
- [ ] Summary: "N policies generated, M approved"
- [ ] Approval notice: "Policies require admin approval to apply"
- [ ] Next button always enabled

#### Step 10: Estimate Costs _(45 min)_
**File**: `apps/web/src/app/onboarding/step10/page.tsx`
- [ ] StepHeader: "Cost Estimation" / "Understand your BigQuery usage"
- [ ] Auto-fetches cost estimate on mount (useCostEstimate query)
- [ ] Display KPI tiles:
  - Cost per query (large number, $X.XX format)
  - Estimated monthly cost (large number, $XXX.XX format)
  - Average bytes scanned per query (formatted: "1.2 GB")
- [ ] Explanation text: "Based on your top 10 largest tables, assuming 10% data scans"
- [ ] Verification section:
  - Button: "Run Verification Queries" (calls useTriggerVerification)
  - JobProgressCard: Shows verification progress
  - Result: Table with columns: Table Name, Bytes Scanned, Dry-run Status (✓)
  - Summary: "Verified N tables, total X GB scanned (dry-run)"
- [ ] Next button always enabled

#### Step 11: Configure Preferences _(30 min)_
**File**: `apps/web/src/app/onboarding/step11/page.tsx`
- [ ] StepHeader: "Workspace Preferences" / "Customize your workspace"
- [ ] Auto-generates preferences on mount (useGeneratePreferences mutation)
- [ ] Form inputs (pre-filled with generated values, user can override):
  - Default view type: Radio buttons (Analytical / Operational / Strategic)
  - Date format: Dropdown (YYYY-MM-DD / MM/DD/YYYY / DD-MM-YYYY)
  - Timezone: Dropdown (America/Chicago, America/New_York, UTC, etc.)
  - Number format: Dropdown (1,234.56 / 1.234,56 / 1 234.56)
  - Theme: Radio buttons (Light / Dark / System)
- [ ] Save button: "Save Preferences" (calls useUpdatePreferences mutation)
- [ ] Success message: "Preferences saved" (green checkmark)
- [ ] Next button always enabled

#### Step 12: Generate Report _(45 min)_ - HTML Summary Only
**File**: `apps/web/src/app/onboarding/step12/page.tsx`
- [ ] StepHeader: "Onboarding Summary" / "Review your setup"
- [ ] Generate button: "Generate Summary" (calls useGenerateReport mutation)
- [ ] Loading spinner while generating (may take 5-10 seconds)
- [ ] Report preview (HTML rendered in div with proper styling):
  - Executive Summary section
  - Data Catalog Overview (datasets, tables, size)
  - PII Detection Results (table)
  - Business Goals (table)
  - Governance Recommendations (list)
  - Cost Estimates (KPIs)
  - Checklist with checkmarks (10 items)
- [ ] NOTE: PDF download button removed per user request (no PDF generation in MVP)
- [ ] Next button: "Complete Onboarding" (enabled after report generated)

#### Step 13: Completion & Next Steps _(30 min)_
**File**: `apps/web/src/app/onboarding/step13/page.tsx`
- [ ] StepHeader: "You're All Set!" / "Welcome to Peter"
- [ ] Celebration visual: Large checkmark icon (✓) or confetti animation (optional)
- [ ] Summary statistics (KPI tiles):
  - Datasets connected: N
  - Tables scanned: M
  - PII columns detected: K
  - Business goals mapped: L
- [ ] Next steps section (bulleted list):
  - "Create your first dashboard"
  - "Explore the data catalog"
  - "Invite more team members"
  - "Review governance policies"
- [ ] Action buttons:
  - "Go to Dashboards" (primary button, navigates to /dashboards)
  - "Explore Data Catalog" (secondary button, navigates to /datasets)
- [ ] Clears onboarding session storage on mount

### 0.5 Routing & Navigation _(1 hour)_
**File**: `apps/web/src/app/onboarding/layout.tsx`
- [ ] 0.5.1 Create onboarding layout with OnboardingLayout component
- [ ] 0.5.2 Implement route structure: /onboarding/step1 through /onboarding/step13
- [ ] 0.5.3 Add middleware: Redirect to step 1 if accessing /onboarding root
- [ ] 0.5.4 Add step validation: Prevent jumping to step N if step N-1 not completed (except via jumpToStep)
- [ ] 0.5.5 Add exit confirmation dialog: "Are you sure? Progress will be saved." (if user clicks Exit button)
- [ ] 0.5.6 Add navigation guard: Warn if user tries to navigate away with unsaved changes (beforeunload event)

### 0.6 Accessibility & Responsive Design _(1 hour)_
- [ ] 0.6.1 Keyboard navigation: All form inputs, buttons, and interactive elements accessible via Tab
- [ ] 0.6.2 Focus indicators: 2px solid ring on all interactive elements (black in light mode, white in dark mode)
- [ ] 0.6.3 ARIA labels: All buttons, inputs, and icons have descriptive aria-label or aria-labelledby
- [ ] 0.6.4 Screen reader announcements: Step changes announce "Step N of 13: [Step Title]"
- [ ] 0.6.5 Color contrast: All text meets WCAG AA (4.5:1 for body, 3:1 for large text)
- [ ] 0.6.6 Mobile responsive: Sidebar and help panel collapse to modals on <1024px
- [ ] 0.6.7 Touch targets: All buttons and clickable areas min 44x44px on mobile
- [ ] 0.6.8 Test with NVDA/JAWS: Verify entire flow navigable with screen reader

### 0.7 Testing _(2 hours)_
- [ ] 0.7.1 Unit test: OnboardingStore state mutations (nextStep, previousStep, setTeam, etc.)
- [ ] 0.7.2 Unit test: canProceed() validation logic for each step
- [ ] 0.7.3 Unit test: sessionStorage persistence (saveToSession, loadFromSession)
- [ ] 0.7.4 Component test: FileUpload component (drag-drop, file validation, error states)
- [ ] 0.7.5 Component test: JobProgressCard component (progress bar updates, status icons)
- [ ] 0.7.6 Component test: ReviewTable component (sorting, approve/reject actions)
- [ ] 0.7.7 Component test: ConfidenceBadge component (color coding for different confidence ranges)
- [ ] 0.7.8 Integration test: Step 1-2 flow (create team → invite members)
- [ ] 0.7.9 Integration test: Step 3-4 flow (upload connection → validate → scan catalog with job polling)
- [ ] 0.7.10 Integration test: Step 5 flow (PII detection job → review table → approve/reject)
- [ ] 0.7.11 E2E test: Full 13-step onboarding flow (happy path with all steps completed)
- [ ] 0.7.12 E2E test: Skip optional steps (dbt, docs) and complete onboarding
- [ ] 0.7.13 E2E test: Exit and resume onboarding (verify sessionStorage persistence)
- [ ] 0.7.14 E2E test: Error handling (connection validation fails, job fails, network error)
- [ ] 0.7.15 Accessibility test: Run axe-core on all 13 steps, verify 0 violations

### 0.8 Documentation & OpenAPI Integration _(30 min)_
- [ ] 0.8.1 Regenerate TypeScript API client after backend Phase 0 OpenAPI updates: `pnpm run codegen:api-client`
- [ ] 0.8.2 Verify all Phase 0 types available in packages/api-client/generated/
- [ ] 0.8.3 Document onboarding flow in apps/web/README.md
- [ ] 0.8.4 Add onboarding screenshots to docs (wireframes or actual screenshots)
- [ ] 0.8.5 Create developer guide: "How to add a new onboarding step"
- [ ] 0.8.6 Update CLAUDE.md with Phase 0 onboarding details

**Phase 0 Deliverables**:
- ✅ Zustand onboarding store with 20+ state fields + sessionStorage persistence
- ✅ 20+ custom TanStack Query hooks for all Phase 0 API endpoints
- ✅ Job polling pattern with progress updates (2-second intervals)
- ✅ 6 shared components (OnboardingLayout, StepHeader, FileUpload, JobProgressCard, ConfidenceBadge, ReviewTable)
- ✅ 13 step-by-step page components (Step1-Step13)
- ✅ Monotone theme compliance (black/white/grey palette, semantic colors only for confidence badges)
- ✅ Full keyboard navigation + WCAG AA accessibility compliance
- ✅ Responsive design (mobile, tablet, desktop breakpoints)
- ✅ E2E test coverage for full onboarding flow
- ✅ OpenAPI TypeScript client integration

---

# 📊 FRONTEND IMPLEMENTATION PRIORITY & READINESS MATRIX

**Last Updated**: 2025-11-03
**Status**: Reprioritized based on backend readiness analysis

## 🎯 Implementation Priority Order

### **TIER 1: IMMEDIATE - Zero Backend Blockers (Weeks 1-3)**
Execute these phases NOW. They work with file-based YAML or simple endpoints.

| Phase | Description | Backend Dependency | Status |
|-------|-------------|-------------------|--------|
| **Phase 3.2** | Dashboard Widgets (minus auto-refresh) | None (use static YAML files) | ✅ Ready |
| **Phase 4** | Dashboard Pages & Data Fetching | Optional: `GET /data/:slug` | ✅ Ready |
| **Phase 5** | YAML Editor & Builder | `POST /dashboards` (simple save) | ✅ Ready |
| **Phase 7** | Lineage Visualization | Mock JSON initially | ✅ Ready |

### **TIER 2: STUB IMPLEMENTATION - Partial Backend (Week 4)**
Build UI shell with mocked data. Full integration deferred.

| Phase | Description | Backend Blocker | Defer Until |
|-------|-------------|-----------------|-------------|
| **Phase 1.5** | Chat UI Components (STUB ONLY) | Universal AI SDK + GCS storage | Month 2-3 |
| **Phase 0-MVP** | Minimal Onboarding (6 steps) | Simple catalog endpoints | Week 2 |

### **TIER 3: DEFERRED - Critical Backend Missing (Month 2-3+)**
Do NOT implement until backend capabilities ship.

| Phase | Description | Backend Blocker | Why Deferred |
|-------|-------------|-----------------|--------------|
| **Phase 6** | LLM Dashboard Creation | Session manifest + artifact pipeline + tool orchestration | Requires system_alignment.md Universal AI SDK work |
| **Phase 3.2.6** | Auto-Refresh & Alerts | Alert feed + cache bust events | No alerting bus exists |
| **Phase 0 Full** | 13-Step Onboarding | 30+ endpoints + polling loops + PII/doc/policy services | Out of MVP scope, backend not ready |

---

## 🚧 Backend Readiness Gates

### Gate 1: Dashboard Rendering ✅ OPEN
**Required**:
- Static YAML files in `/dashboards/` directory (Git-based storage)
- OR single endpoint: `GET /data/:slug` returning chart data

**Status**: ✅ File system access works, can proceed

---

### Gate 2: YAML Persistence ⚠️ SIMPLE
**Required**:
- `POST /dashboards` - Save new dashboard YAML
- `PUT /dashboards/:id` - Update existing dashboard
- Validation endpoint (optional): `POST /dashboards/validate`

**Status**: ⚠️ Need to add, low complexity (2-3 hours backend work)

---

### Gate 3: Minimal Onboarding ⚠️ MODERATE
**Required**:
- `POST /connections/test` - Validate BigQuery credentials
- `GET /catalog/datasets` - List available datasets
- `GET /catalog/tables/:id/schema` - Get table schema

**Status**: ⚠️ Need to add, moderate complexity (1 day backend work)

---

### Gate 4: Lineage Graph ❌ BLOCKED
**Required**:
- `GET /lineage/:slug` - Return graph JSON (nodes + edges)

**Status**: ❌ Not prioritized yet, use mock JSON for now

---

### Gate 5: Chat & AI Features ❌ BLOCKED
**Required** (from system_alignment.md):
- Universal AI SDK layer (Python)
- Session manifest table (Postgres metadata)
- GCS-backed message store (append JSONL chunks)
- Artifacts table (index) + Tool cache table
- `/chat` SSE endpoint streaming `text`, `tool_call`, `cost_update` events
- `/sessions/current` - Session metadata (cost, tokens, provider)
- `/sessions/:id/messages` - Message history

**Status**: ❌ Major backend work, 2-3 weeks, defer Phase 1.5 full integration

---

### Gate 6: Auto-Refresh & Alerting ❌ BLOCKED
**Required**:
- Alert feed (Pub/Sub or WebSocket)
- Cache invalidation events
- `/alerts/:dashboard_id` - Active alerts endpoint

**Status**: ❌ Alerting bus not in roadmap, defer indefinitely

---

## 📝 Removed/Reduced Scope Items

### ❌ Phase 0 Bloat REMOVED
**Original**: 13-step wizard with PII detection, doc crawl, policy approval, business goal mapping, cost verification, summary report generation

**Why Removed**:
- Onboarding state store pulls almost every backend domain object into client (contradicts thin presentation layer principle)
- ~30 bespoke endpoints + multiple 2s polling loops would hammer server
- Services (goal mapping, doc crawl, verification) are aspirational, not implemented
- Out of MVP scope ("deliver dashboards + chat")

**New Scope**: 6-step minimal onboarding (team name, connection test, catalog scan only)

---

### ❌ Auto-Refresh REMOVED from Phase 3.2
**Original**: 30s polling loop with alert banners, per-chart freshness updates

**Why Removed**:
- No backend alert feed or cache invalidation bus
- Would hammer BigQuery with continuous refreshes
- Operational dashboard features deferred to post-MVP

**New Scope**: Manual refresh button only

---

### ⚠️ Phase 1.5 STUBBED
**Original**: Full Vercel AI SDK integration with real SSE streaming

**Why Stubbed**:
- Backend Universal AI SDK not ready (needs GCS storage, session manifest, artifact pipeline)
- Cannot test real chat without `/chat` endpoint and session APIs

**New Scope**: UI components with hardcoded mock messages, no real SSE

---

### ❌ Phase 6 DEFERRED
**Original**: Full LLM dashboard creation, SQL verification display, iterative refinement, "Explain this"

**Why Deferred**:
- Requires session manifest + GCS artifact pipeline + tool orchestration
- Depends on Phase 1.5 full implementation
- Post-MVP feature (Month 2-3)

**New Scope**: Not implemented in initial sprint

---

## 🗓️ Revised Sprint Plan

### Sprint 1: Dashboard Foundation (Days 1-5)
```
✅ Phase 3.2 (minus auto-refresh): Dashboard widgets, grid layout, freshness indicators
✅ Phase 4.1-4.3: TanStack Query hooks, gallery page, dashboard view page
✅ File-based YAML loading from /dashboards/ directory
✅ Static or single-endpoint data fetching
```

**Deliverables**: Working dashboard gallery + view, YAML rendering, charts display

---

### Sprint 2: YAML Editor (Days 6-10)
```
✅ Phase 5.1-5.3: YAML parser, validation, editor tabs (Builder/YAML/Preview)
✅ Two-way sync: UI edits → YAML file → preview updates
✅ File save (needs POST /dashboards endpoint - 2h backend work)
```

**Deliverables**: Full YAML editing workflow, dirty state tracking, save

---

### Sprint 3: Onboarding MVP (Days 11-13)
```
✅ Phase 0-MVP: 6-step minimal onboarding
   - Step 1: Team name
   - Step 2-3: Skip (use defaults)
   - Step 4: BigQuery connection test
   - Step 5: Dataset discovery
   - Step 6: Table schema preview
✅ Simplified onboarding store (no PII/docs/policies)
✅ Single-session completion (no save/resume)
```

**Deliverables**: Working onboarding, connection validation, catalog browsing

---

### Sprint 4: Lineage + Polish (Days 14-15)
```
✅ Phase 7: Lineage graph UI (mock JSON data)
✅ Accessibility audit (WCAG AA)
✅ Responsive testing (mobile, tablet, desktop)
✅ Performance optimization (Lighthouse >90)
```

**Deliverables**: Lineage visualization, accessibility compliance, polish

---

### Sprint 5: Chat UI Stub (Day 16) ⚠️ STUB ONLY
```
⚠️  Chat components with hardcoded mock messages
⚠️  No real Vercel AI SDK integration
⚠️  No SSE streaming
⚠️  UI shell for demo only
```

**Deliverables**: Chat panel renders, shows mock conversation, demonstrates UX

---

## Phase 1: Foundation & Setup ✅ COMPLETE
**Days 1-3 | Completed 2025-10-29**

### 1.1 Monorepo & TypeScript Setup
- [x] 1.1.1 Root package.json with pnpm workspaces
- [x] 1.1.2 Root tsconfig.json with strict mode
- [x] 1.1.3 Update docker-compose.yml with web service
- [x] 1.1.4 Makefile commands for web dev workflow

### 1.2 Next.js Application Scaffolding
- [x] 1.2.1 Init Next.js 15 at apps/web/ (Next.js 16.0.1 with React 19)
- [x] 1.2.2 Tailwind CSS configuration with monotone theme
- [x] 1.2.3 ShadCN/UI setup and initialization
- [x] 1.2.4 Install core dependencies: TanStack Query, Zustand, Recharts, Lucide, js-yaml
- [x] 1.2.5 Configure next.config.js (API proxy to :8000, output config)

### 1.3 Design System & UI Foundation
- [x] 1.3.1 Monotone color palette in globals.css (HSL grey scale: 10-90%)
- [x] 1.3.2 ShadCN components installed: Button, Card, Input, Dialog, Tabs, Sheet, Sonner, ScrollArea, Alert
- [x] 1.3.3 ThemeProvider configured (light/dark mode support)
- [x] 1.3.4 Inter font integration + typography utilities
- [x] 1.3.5 CSS custom properties for theme variables

**Deliverables**: 32 files created, ~2,100 lines of code
**Documentation**: `/docs/frontend_phase1_completion.md`

---

## Phase 1.5: Universal AI SDK Chat Integration 📝 PLANNED
**Estimated: Days 7-10 | Depends on backend `/chat` and `/sessions` endpoints**

**Purpose**: Integrate Vercel AI SDK for chat UI consuming backend's Universal AI SDK. Frontend acts as pure display layer—backend handles all LLM calls, provider selection, tool execution, session storage (GCS), and cost tracking. This phase establishes foundation for Phase 6 (LLM Chat Assistant features).

### 1.5.1 Vercel AI SDK Setup & Configuration
**Complexity**: Simple | **Files**: `apps/web/package.json`, `apps/web/lib/api/chat-client.ts`

- [ ] 1.5.1.1 Install dependencies: `pnpm add ai`
- [ ] 1.5.1.2 Create `lib/api/chat-client.ts` with `useChat()` configuration
- [ ] 1.5.1.3 Configure SSE endpoint: `api: '/api/v1/chat'` with session ID in body
- [ ] 1.5.1.4 Add environment variable: `NEXT_PUBLIC_CHAT_API_URL`
- [ ] 1.5.1.5 Test basic streaming with mock backend response (curl or Postman)
- [ ] 1.5.1.6 Verify SSE connection establishes correctly (check Network tab DevTools)

**Acceptance Criteria**:
- `useChat()` hook returns messages, append, isLoading correctly
- SSE connection visible in DevTools Network tab
- Messages stream progressively (not all at once)

---

### 1.5.2 Session Store Implementation (Zustand)
**Complexity**: Medium | **Files**: `apps/web/lib/stores/session-store.ts`, `apps/web/lib/api/session-client.ts`

- [ ] 1.5.2.1 Create Zustand store: `lib/stores/session-store.ts`
- [ ] 1.5.2.2 Store state: `{ sessionId, user, provider, totalCost, totalTokens, isHydrated }`
- [ ] 1.5.2.3 Implement `hydrate()` action calling `GET /sessions/current`
- [ ] 1.5.2.4 Implement `updateCost(cost, tokens)` and `addMessage(message)` actions
- [ ] 1.5.2.5 Wire up hydration in `app/layout.tsx` (call on mount)
- [ ] 1.5.2.6 Add loading state during hydration
- [ ] 1.5.2.7 Handle hydration errors (session expired → redirect to login)

**Acceptance Criteria**:
- Store hydrates on app mount with current session data from backend
- Cost/tokens update correctly after simulated message (manual test)
- Store persists across route changes (memory only, cleared on page close)
- Hydration errors trigger login redirect

---

### 1.5.3 Chat Interface Components
**Complexity**: Complex | **Files**: `apps/web/components/assistant/*.tsx`

#### 1.5.3.1 ChatContainer Component
- [ ] Create `components/assistant/ChatContainer.tsx`
- [ ] Resizable right panel (320px default, 200-600px range)
- [ ] Collapsible with toggle button
- [ ] Header with title "Assistant" and close button

#### 1.5.3.2 MessageList Component
- [ ] Create `components/assistant/MessageList.tsx`
- [ ] Virtualized list using `react-window` for >100 messages
- [ ] Auto-scroll to bottom on new messages
- [ ] "Jump to latest" button when scrolled up >100px
- [ ] Loading skeleton while fetching history

#### 1.5.3.3 MessageBubble Component
- [ ] Create `components/assistant/MessageBubble.tsx`
- [ ] Role-based styling: user (right-aligned, dark bg), assistant (left-aligned, light grey)
- [ ] Display timestamp as relative time ("2m ago")
- [ ] Per-message cost badge (small pill, grey, next to timestamp)
- [ ] Support inline tool call cards (see 1.5.4)

#### 1.5.3.4 InputArea Component
- [ ] Create `components/assistant/InputArea.tsx`
- [ ] Auto-resize textarea (min 40px, max 200px)
- [ ] Send button (disabled when empty or loading)
- [ ] Keyboard shortcut: Cmd/Ctrl+Enter to send
- [ ] Character count display (optional, for token estimation later)

#### 1.5.3.5 Wire Up useChat Hook
- [ ] Import and initialize `useChat()` in ChatContainer
- [ ] Pass messages to MessageList
- [ ] Connect InputArea to `append()` function
- [ ] Handle loading state (disable input, show typing indicator)

**Acceptance Criteria**:
- Chat panel opens/closes smoothly
- Messages render with correct alignment (user right, assistant left)
- Virtualization works smoothly for >100 messages (test with mock data)
- Input area auto-resizes and sends messages via `append()`
- Monotone theme applied throughout (no colors except semantic status)

---

### 1.5.4 Tool Execution Display Components
**Complexity**: Complex | **Files**: `apps/web/components/assistant/tool/*.tsx`

#### 1.5.4.1 ToolCallCard Component
- [ ] Create `components/assistant/tool/ToolCallCard.tsx`
- [ ] Display tool name, collapsed args preview
- [ ] State machine: `pending` → `executing` → `completed` | `failed`
- [ ] Pending: greyed out, no interaction
- [ ] Executing: spinner, "Running..." text
- [ ] Completed: green checkmark, expandable result panel
- [ ] Failed: red X, error message

#### 1.5.4.2 ToolResultPanel Component
- [ ] Create `components/assistant/tool/ToolResultPanel.tsx`
- [ ] Collapsible panel below ToolCallCard
- [ ] Syntax-highlighted JSON/code results (use ShadCN CodeBlock or similar)
- [ ] Copy button for result content
- [ ] Max height with scroll for large results

#### 1.5.4.3 Integrate with Message Stream
- [ ] Parse `tool_call` events from SSE stream
- [ ] Render ToolCallCard inline within assistant MessageBubble
- [ ] Update card state as `tool_status` events arrive
- [ ] Expand result panel automatically on completion

**Acceptance Criteria**:
- Tool call appears inline in assistant message
- Card transitions correctly through states (pending → executing → completed)
- Result streams progressively into panel
- Failed tools show error message clearly
- No approval UI (backend handles orchestration in MVP)

---

### 1.5.5 Cost & Token Tracking UI
**Complexity**: Medium | **Files**: `apps/web/components/assistant/CostCounter.tsx`

#### 1.5.5.1 CostCounter Component
- [ ] Create `components/assistant/CostCounter.tsx`
- [ ] Read from session store: `totalCost`, `totalTokens`
- [ ] Display format: "$1.23 • 45.2K tokens"
- [ ] Position in assistant panel header (top-right)
- [ ] Color-coded warnings: green (<$1), yellow ($1-5), red (>$5)
- [ ] Tooltip with breakdown (input tokens, output tokens, cost per message type)

#### 1.5.5.2 Per-Message Cost Badge
- [ ] Add cost prop to MessageBubble component
- [ ] Display as small pill next to timestamp: "$0.0023"
- [ ] Use monotone grey (not semantic color)
- [ ] Only show if cost > $0

#### 1.5.5.3 Budget Warning Banner
- [ ] Create `components/assistant/BudgetWarning.tsx`
- [ ] Trigger at 80% of daily budget (read from session metadata)
- [ ] Display above input area
- [ ] Message: "Approaching daily budget ($8/$10). Monitor usage."
- [ ] Dismissible, but re-appears if cost increases

#### 1.5.5.4 Update Cost on SSE Events
- [ ] Listen for `cost_update` events in SSE stream
- [ ] Call `sessionStore.updateCost(cost, tokens)` on event
- [ ] CostCounter re-renders automatically (Zustand subscription)

**Acceptance Criteria**:
- Counter updates in real-time as messages complete
- Cost displayed with 4 decimal places (e.g., $0.0023)
- Token count shows input/output breakdown in tooltip
- Warning banner appears at correct threshold (test with mock session over limit)
- All values from backend—no frontend calculation

---

### 1.5.6 Provider Display (Read-Only)
**Complexity**: Simple | **Files**: `apps/web/components/assistant/ProviderIndicator.tsx`

- [ ] 1.5.6.1 Create `components/assistant/ProviderIndicator.tsx`
- [ ] 1.5.6.2 Read `session.provider` from session store
- [ ] 1.5.6.3 Display in chat header: "Using Claude 3.5 Sonnet"
- [ ] 1.5.6.4 Monotone styling (grey text, small font)
- [ ] 1.5.6.5 No selection dropdown (backend chooses provider)
- [ ] 1.5.6.6 Tooltip: "Provider selected by backend based on task"

**Acceptance Criteria**:
- Provider name displayed correctly from session metadata
- Updates when provider changes (edge case, not in MVP)
- Read-only (no interaction)
- Tooltip explains backend selection

---

### 1.5.7 Chat Store Implementation (Zustand)
**Complexity**: Medium | **Files**: `apps/web/lib/stores/chat-store.ts`

- [ ] 1.5.7.1 Create Zustand store: `lib/stores/chat-store.ts`
- [ ] 1.5.7.2 Store state: `{ messages, pendingTools, optimisticMessages }`
- [ ] 1.5.7.3 Implement `addOptimisticMessage(content)` (temp ID, user role)
- [ ] 1.5.7.4 Implement `confirmMessage(tempId, realId)` (replace temp with real from backend)
- [ ] 1.5.7.5 Implement `addPendingTool(tool)` and `updateToolStatus(id, status)`
- [ ] 1.5.7.6 Sync with Vercel AI SDK's internal state (messages array)

**Acceptance Criteria**:
- Optimistic messages appear immediately on send
- Messages update from temp ID to real ID on backend confirmation
- Pending tools tracked correctly
- Store syncs with `useChat()` messages

---

### 1.5.8 Message Caching (TanStack Query)
**Complexity**: Medium | **Files**: `apps/web/lib/hooks/useMessages.ts`, `apps/web/lib/api/query-client.ts`

- [ ] 1.5.8.1 Add TanStack Query cache for messages
- [ ] 1.5.8.2 Cache key pattern: `['session', sessionId, 'messages']`
- [ ] 1.5.8.3 Fetch from `GET /sessions/:id/messages` on mount
- [ ] 1.5.8.4 Set stale time to Infinity (messages immutable)
- [ ] 1.5.8.5 Invalidate cache on new SSE message (prevent drift)
- [ ] 1.5.8.6 Implement optimistic update for new messages (instant UI, rollback on error)
- [ ] 1.5.8.7 Garbage collect old sessions after 30 minutes

**Acceptance Criteria**:
- Messages cached and don't refetch unnecessarily
- Cache hydrates from backend on panel open
- New messages from SSE invalidate and refresh cache
- Optimistic updates work (message appears instantly, updates with real data)
- Old sessions clear from cache after timeout

---

### 1.5.9 Error Handling & Display
**Complexity**: Medium | **Files**: `apps/web/components/assistant/ErrorBanner.tsx`, `apps/web/lib/errors/chat-errors.ts`

#### 1.5.9.1 Error Banner Component
- [ ] Create `components/assistant/ErrorBanner.tsx`
- [ ] Display above input area (red background, white text)
- [ ] Show error message from backend
- [ ] "Retry" button if error is retryable (read from backend error metadata)
- [ ] "Copy error details" button (includes trace ID)
- [ ] Auto-dismiss after 10 seconds (unless user interacts)

#### 1.5.9.2 Error Handling in useChat
- [ ] Add `onError` callback to `useChat()` configuration
- [ ] Parse error response from backend (JSON format)
- [ ] Display error in ErrorBanner
- [ ] Log error to console (with trace ID)

#### 1.5.9.3 Network Error Handling
- [ ] Detect SSE connection drops (EventSource error event)
- [ ] Show "Reconnecting..." toast
- [ ] Auto-reconnect with exponential backoff (3 attempts)
- [ ] On success, resume stream from last message

#### 1.5.9.4 Session Expired Handling
- [ ] Detect 401 responses
- [ ] Redirect to login immediately
- [ ] No draft preservation in MVP (backend is source of truth)

**Acceptance Criteria**:
- Backend errors display in banner with clear message
- Retry button works for retryable errors
- Network errors trigger reconnect logic
- Session expired redirects to login
- All error states tested (mock error responses)

---

### 1.5.10 Streaming UX Enhancements
**Complexity**: Medium | **Files**: Various component updates

- [ ] 1.5.10.1 Add typing indicator while waiting for first token
- [ ] 1.5.10.2 Progressive text rendering (word-by-word via Vercel SDK)
- [ ] 1.5.10.3 Tool call cards appear inline during stream
- [ ] 1.5.10.4 Auto-scroll follows latest message (unless user scrolled manually)
- [ ] 1.5.10.5 "Stop generation" button while streaming (calls `stop()` from useChat)
- [ ] 1.5.10.6 Disable input while generating
- [ ] 1.5.10.7 Smooth transitions between states (pending → typing → complete)

**Acceptance Criteria**:
- Typing indicator appears immediately on send
- Text streams smoothly (not janky, ~60 FPS)
- Tool calls render inline as they arrive
- Auto-scroll works correctly (doesn't scroll if user has scrolled up)
- Stop button cancels stream and re-enables input

---

### 1.5.11 Integration Testing (E2E)
**Complexity**: Complex | **Files**: `apps/web/tests/e2e/chat.spec.ts`

- [ ] 1.5.11.1 E2E test: Open chat → Send message → Verify streaming
- [ ] 1.5.11.2 E2E test: Send message with tool call → Verify status updates → Verify result displays
- [ ] 1.5.11.3 E2E test: Trigger backend error → Verify error banner → Retry
- [ ] 1.5.11.4 E2E test: Send 5 messages → Verify cost increments correctly
- [ ] 1.5.11.5 E2E test: Session recovery → Disconnect network → Reconnect → Verify messages persist
- [ ] 1.5.11.6 E2E test: Cost warning banner → Mock session over 80% budget → Verify banner appears
- [ ] 1.5.11.7 E2E test: Provider display → Verify correct provider shown from backend

**Acceptance Criteria**:
- All E2E tests pass in Playwright
- Chat interaction completes end-to-end with real backend
- Tool execution flow works without errors
- Error states render correctly
- Cost tracking accurate (matches backend session endpoint response)
- Tests run in CI pipeline

---

**Phase 1.5 Deliverables**:
- Vercel AI SDK integrated and streaming from backend `/chat`
- Session store hydrating from `/sessions/current`
- Chat UI components (MessageList, MessageBubble, InputArea, ToolCallCard, CostCounter)
- Message caching via TanStack Query
- Error handling for network, backend errors, session expiry
- E2E tests covering happy path and error scenarios

**Phase 1.5 Blockers**:
- Backend `/chat` endpoint must support SSE streaming
- Backend `/sessions/current` and `/sessions/:id/messages` endpoints functional
- Backend must emit `cost_update` and `tool_call` events in SSE stream

**Phase 1.5 Success Criteria**:
- User can send message and see progressive streaming response
- Tool calls display with correct status (pending → executing → completed)
- Cost counter updates in real-time
- Session persists across route changes
- All E2E tests green

---

## Phase 2: OpenAPI Client & Auth ✅ COMPLETE
**Days 4-6 | Completed 2025-10-29**

### 2.1 API Client Generation & Integration
- [x] 2.1.1 packages/api-client/ workspace for generated code
- [x] 2.1.2 Codegen script using openapi-typescript-codegen
- [x] 2.1.3 Run codegen from backend OpenAPI spec (openapi.yaml)
- [x] 2.1.4 lib/api-client.ts wrapper with interceptors and error handling
- [x] 2.1.5 TanStack Query provider with generated types
- [x] 2.1.6 React Query DevTools integration

### 2.2 Authentication Flow
- [x] 2.2.1 Login page (app/login/page.tsx) with Google OAuth redirect
- [x] 2.2.2 middleware.ts for protected route session validation
- [x] 2.2.3 SessionContext provider with user state
- [x] 2.2.4 Auth utilities: getSession(), logout(), checkAuth()
- [x] 2.2.5 Session cookie handling (HTTP-only, Secure, SameSite)
- [x] 2.2.6 Logout flow with session cleanup

### 2.3 Application Shell (3-Panel Layout)
- [x] 2.3.1 Root layout (app/layout.tsx) with QueryClientProvider, SessionProvider, ThemeProvider
- [x] 2.3.2 AppShell component (components/layout/app-shell.tsx) with responsive behavior
- [x] 2.3.3 Explorer sidebar (240px fixed, collapsible on mobile)
- [x] 2.3.4 Workspace center panel with ScrollArea wrapper
- [x] 2.3.5 Assistant panel (320px fixed, collapsible, chat stub for Phase 6)
- [x] 2.3.6 AppHeader with breadcrumbs, user menu, theme toggle, logout
- [x] 2.3.7 Responsive collapse behavior (<1024px)

### 2.4 Route Structure & Error Handling
- [x] 2.4.1 Route scaffolding: /dashboards, /dash/[slug], /edit/[slug], /lineage/[slug], /settings, /help
- [x] 2.4.2 loading.tsx skeleton components per route
- [x] 2.4.3 error.tsx error boundaries per route
- [x] 2.4.4 not-found.tsx for 404 handling

**Deliverables**: 23 files created, ~1,400 lines of code
**Documentation**: `/docs/frontend_phase2_completion.md`

---

## Phase 3: Charts & Dashboard Widgets
**Days 7-12**

### Phase 3.1: Chart Components ✅ COMPLETE
**Completed 2025-10-30**

- [x] 3.1.1 ChartContainer wrapper (loading/error/empty states)
- [x] 3.1.2 LineChart component (Recharts, monotone theme)
- [x] 3.1.3 BarChart component (horizontal/vertical orientation)
- [x] 3.1.4 AreaChart component (stacked areas, 60% opacity)
- [x] 3.1.5 TableChart component (sortable, responsive columns)
- [x] 3.1.6 KPITile component (large format, delta indicators, trending icons)
- [x] 3.1.7 ChartRenderer factory (type-safe switch with exhaustive checking)
- [x] 3.1.8 ChartSkeleton loading states (integrated in ChartContainer)
- [x] 3.1.9 Chart error states (Alert variant with retry)
- [x] 3.1.10 Monotone theme applied (grey gradients HSL 0 0% 10-90%, semantic colors for data only)
- [x] 3.1.11 Table UI primitives (Table, TableHeader, TableBody, TableRow, TableHead, TableCell)
- [x] 3.1.12 Chart exports via index.ts barrel file

**Deliverables**: 8 files created, ~950 lines of code
**Documentation**: `/docs/frontend_phase3_completion.md`

### Phase 3.2: Dashboard Widget Components 🚧 IN PROGRESS
**Estimated: Days 11-12**

#### 3.2.1 Dashboard Card Component
- [ ] 3.2.1.1 DashboardCard skeleton (Card with hover effects)
- [ ] 3.2.1.2 Dashboard thumbnail preview (optional image or chart icons)
- [ ] 3.2.1.3 Metadata display: title, owner, last updated
- [ ] 3.2.1.4 Tag chips with monotone styling
- [ ] 3.2.1.5 Click navigation to /dash/[slug]
- [ ] 3.2.1.6 Hover state with elevated shadow
- [ ] 3.2.1.7 Empty state for "No dashboards"

#### 3.2.2 Freshness Indicator Component
- [ ] 3.2.2.1 FreshnessIndicator badge component
- [ ] 3.2.2.2 Color coding logic: green (<1h), yellow (1-4h), red (>4h), grey (unknown)
- [ ] 3.2.2.3 Tooltip with full timestamp and source table
- [ ] 3.2.2.4 "As of" timestamp formatting (relative time)
- [ ] 3.2.2.5 Global dashboard freshness (header)
- [ ] 3.2.2.6 Per-chart freshness (card footer)

#### 3.2.3 Filter Panel Component
- [ ] 3.2.3.1 FilterPanel container (collapsible section)
- [ ] 3.2.3.2 Date range selector (Last 7d, 30d, 90d, YTD, custom)
- [ ] 3.2.3.3 Multi-select dropdowns for categorical filters
- [ ] 3.2.3.4 Active filter chips with remove (X) button
- [ ] 3.2.3.5 Clear all filters button
- [ ] 3.2.3.6 Filter state in URL query params
- [ ] 3.2.3.7 Apply button with loading state

#### 3.2.4 Chart Grid Layout
- [ ] 3.2.4.1 ChartGrid component (12-column responsive grid)
- [ ] 3.2.4.2 Grid item positioning from YAML (row, col, width, height)
- [ ] 3.2.4.3 Responsive breakpoints: mobile (1 col), tablet (2-3 col), desktop (12 col)
- [ ] 3.2.4.4 Gap/gutter configuration (16px mobile, 24px desktop)
- [ ] 3.2.4.5 Overflow handling for long dashboards
- [ ] 3.2.4.6 Scroll behavior (smooth scroll to anchor)

#### 3.2.5 View Type Components
- [ ] 3.2.5.1 ViewTypeSwitcher component (Analytical/Operational/Strategic toggle)
- [ ] 3.2.5.2 Analytical view layout template (multi-column, prominent filters)
- [ ] 3.2.5.3 Operational view layout template (KPIs above fold, alert banners)
- [ ] 3.2.5.4 Strategic view layout template (large KPIs, narrative text blocks)
- [ ] 3.2.5.5 View type state persistence (URL param)
- [ ] 3.2.5.6 Layout density differences per view type

#### 3.2.6 Operational View Refresh & Alerts (PDR UI §3)
- [ ] 3.2.6.1 Implement 30s auto-refresh loop for Operational dashboards _(Notes: Pause when tab hidden; configurable interval per YAML metadata)_
- [ ] 3.2.6.2 Display active alert banner & KPI status icons _(Notes: Consume backend status feed; match UI spec for alert badges)_
- [ ] 3.2.6.3 Surface "Next refresh" timestamp + manual pause control _(Notes: Align with operational wireframes in `ui_pdr.md`)_

**Phase 3.2 Acceptance Criteria**:
- DashboardCard displays metadata correctly
- Freshness indicators show correct color coding
- Filters apply to all widgets and update URL
- Grid layout matches YAML position specifications
- View type switcher changes layout density

---

## Phase 4: Dashboard Pages & Data Fetching
**Days 13-16**

### 4.1 TanStack Query Hooks & Data Layer
- [ ] 4.1.1 TanStack Query client configuration (staleTime, cacheTime, retry)
- [ ] 4.1.2 useDashboards hook (GET /v1/dashboards) with pagination
- [ ] 4.1.3 useDashboard hook (GET /v1/dashboards/{slug}) for metadata
- [ ] 4.1.4 useDashboardData hook (GET /v1/data/{slug}) for chart payloads
- [ ] 4.1.5 useLineage hook (GET /v1/lineage/{slug}) for graph data
- [ ] 4.1.6 usePrecompute mutation (POST /v1/precompute) for cache warming
- [ ] 4.1.7 Caching strategy: staleTime (5min metadata, 10min data), refetchOnWindowFocus
- [ ] 4.1.8 error-handling.ts with error classification (network, auth, validation, quota, server, client)
- [ ] 4.1.9 Retry logic with exponential backoff (max 3 retries)
- [ ] 4.1.10 Optimistic updates for mutations
- [ ] 4.1.11 Client error logging pipeline to backend telemetry endpoint _(Notes: Include user/session context; fulfills Frontend PDR §7 Logging)_

### 4.2 Dashboard Gallery Page (/dashboards)
- [ ] 4.2.1 Gallery page layout with search input
- [ ] 4.2.2 DashboardCard grid (responsive, 2-4 columns)
- [ ] 4.2.3 Search filter (client-side, by title/owner/tags)
- [ ] 4.2.4 Dropdown filters: owner, tags, view type, date range
- [ ] 4.2.5 "New Dashboard" button (opens modal or redirects to /new)
- [ ] 4.2.6 Empty state with CTA "Create your first dashboard"
- [ ] 4.2.7 Loading skeleton for dashboard cards
- [ ] 4.2.8 Error state with retry button
- [ ] 4.2.9 Pagination or infinite scroll (if >50 dashboards)
- [ ] 4.2.10 Persist gallery filters + view type in URL query params _(Notes: Supports deep linking per UI PDR §4)_
- [ ] 4.2.11 Restore filter state from URL or session on load _(Notes: Ensures explorer consistency)_

### 4.3 Dashboard View Page (/dash/[slug])
- [ ] 4.3.1 Server Component for initial metadata fetch
- [ ] 4.3.2 Client hydration with useDashboardData hook
- [ ] 4.3.3 YAML parser integration (lib/yaml-parser.ts)
- [ ] 4.3.4 ChartGrid layout rendering from YAML
- [ ] 4.3.5 ChartRenderer mapping YAML to React components
- [ ] 4.3.6 Global freshness timestamp in header
- [ ] 4.3.7 Per-chart FreshnessIndicator badges
- [ ] 4.3.8 Manual refresh button (invalidate query cache)
- [ ] 4.3.9 View type toggle (Analytical/Operational/Strategic)
- [ ] 4.3.10 Filter panel integration
- [ ] 4.3.11 Chart kebab menu (⋮): "Explain", "View SQL", "View Lineage"
- [ ] 4.3.12 Loading state (show skeletons while data fetches)
- [ ] 4.3.13 Error boundary with trace ID display
- [ ] 4.3.14 404 handling for missing dashboards
- [ ] 4.3.15 Breadcrumb navigation
- [ ] 4.3.16 Operational view auto-refresh controls (start/stop, interval management) _(Notes: Reuses 3.2.6 loop; integrates with TanStack Query refetch)_
- [ ] 4.3.17 Chart info panel shows verification metadata (bytes scanned, sample stats) _(Notes: Surfaced from backend response per Frontend PDR §8)_

**Phase 4 Acceptance Criteria**:
- Dashboard gallery loads and displays all dashboards
- Search and filters work correctly
- Dashboard view renders all charts with live data
- Freshness indicators visible globally and per-chart
- Manual refresh re-fetches data from backend
- View type switcher changes layout template
- Error states display with actionable messages

---

## Phase 5: YAML Editor & Dashboard Editing
**Days 17-20**

### 5.1 YAML Parsing & Validation
- [ ] 5.1.1 lib/yaml-parser.ts (parse YAML to JSON, handle errors)
- [ ] 5.1.2 lib/yaml-serializer.ts (JSON to YAML with formatting)
- [ ] 5.1.3 types/dashboard.ts (TypeScript types extending generated OpenAPI types)
- [ ] 5.1.4 YAML ↔ React component tree mapping
- [ ] 5.1.5 Client-side validation using Zod or Yup
- [ ] 5.1.6 Backend validation hook (POST /v1/dashboards/validate)
- [ ] 5.1.7 Error message formatting (line numbers, helpful hints)

### 5.2 Editor UI Components (3-Tab Interface)
- [ ] 5.2.1 EditorLayout component (app/edit/[slug]/layout.tsx)
- [ ] 5.2.2 Tab navigation: Builder, YAML, Preview
- [ ] 5.2.3 BuilderTab (visual drag-drop canvas - Phase 1: click-to-edit only)
- [ ] 5.2.4 PropertiesPanel (right sidebar, 280px)
- [ ] 5.2.5 YamlTab with CodeMirror editor (@codemirror/lang-yaml, @codemirror/theme-one-dark)
- [ ] 5.2.6 PreviewTab (renders live dashboard with real data)
- [ ] 5.2.7 EditorHeader with dirty state indicator
- [ ] 5.2.8 Action buttons: Cancel, Validate, Save

### 5.3 Builder Tab (Visual Editor)
- [ ] 5.3.1 Canvas area with widget outlines
- [ ] 5.3.2 Widget selection (click to select, blue outline)
- [ ] 5.3.3 PropertiesPanel content updates on selection
- [ ] 5.3.4 Chart type dropdown (line, bar, area, table, kpi)
- [ ] 5.3.5 Color picker component (monotone palette + semantic colors)
- [ ] 5.3.6 Size radio buttons (S, M, L, XL)
- [ ] 5.3.7 X-axis, Y-axis, Series dropdowns (populated from query schema)
- [ ] 5.3.8 Delete widget button
- [ ] 5.3.9 "Add Widget" button (opens widget type picker)
- [ ] 5.3.10 Instant preview: UI changes update in-memory YAML model

### 5.4 YAML Tab (Code Editor)
- [ ] 5.4.1 CodeMirror editor with YAML syntax highlighting
- [ ] 5.4.2 Line numbers and gutter
- [ ] 5.4.3 Debounced validation on keystroke (300ms)
- [ ] 5.4.4 Inline error highlighting (squiggly underlines)
- [ ] 5.4.5 Error messages in gutter with tooltips
- [ ] 5.4.6 Format button (auto-indent and clean whitespace)
- [ ] 5.4.7 Find/Replace (Cmd/Ctrl+F)
- [ ] 5.4.8 YAML → UI sync: changes update canvas preview

### 5.5 Preview Tab
- [ ] 5.5.1 Full dashboard render with live data
- [ ] 5.5.2 Interactive charts (hover tooltips, legend toggles)
- [ ] 5.5.3 "Preview uses live data" notice
- [ ] 5.5.4 Refresh button to re-fetch data

### 5.6 Save Workflow & Dirty State
- [ ] 5.6.1 Dirty state tracker (Zustand store or React state)
- [ ] 5.6.2 Unsaved changes banner (⚠️ Unsaved changes)
- [ ] 5.6.3 Save confirmation dialog (optional)
- [ ] 5.6.4 Navigation guard (beforeunload event)
- [ ] 5.6.5 Confirmation dialog on navigate with unsaved changes
- [ ] 5.6.6 Save mutation (POST /v1/dashboards/save)
- [ ] 5.6.7 Toast notifications (Sonner): success, error
- [ ] 5.6.8 Optimistic UI update on save
- [ ] 5.6.9 Reset dirty flag after successful save
- [ ] 5.6.10 Last saved timestamp display

**Phase 5 Acceptance Criteria**:
- Can edit dashboard in Builder tab visually
- Properties panel updates when widget selected
- Changes in Builder reflect in YAML tab
- YAML tab edits update Preview tab rendering
- Validation errors shown inline with line numbers
- Save workflow persists changes to backend
- Dirty state prevents accidental navigation

---

## Phase 6: LLM Chat Assistant (Enhanced Features)
**Days 21-23 | Depends on Phase 1.5 completion**

**Note**: Core chat UI (MessageBubble, InputArea, streaming, cost tracking) implemented in Phase 1.5. This phase adds LLM-specific features: dashboard creation, iterative refinement, SQL verification display, "Explain this" functionality.

### 6.1 Dashboard-Specific Chat Components
**Complexity**: Medium | **Files**: `apps/web/components/assistant/dashboard/*.tsx`

- [ ] 6.1.1 ExamplePrompts component (clickable dashboard creation suggestions)
  - Examples: "Show revenue by region", "Track daily signups", "Monitor API latency"
  - Positioned below input area when chat empty
  - Monotone styling (grey cards, hover effect)
- [ ] 6.1.2 DashboardPreviewCard (inline preview in chat)
  - Mini version of dashboard with live charts
  - Rendered within assistant message bubble
  - Click to expand full-size preview
  - "Apply Changes" and "Save Dashboard" buttons
- [ ] 6.1.3 CodeBlock component (syntax-highlighted SQL preview)
  - Shows generated SQL queries
  - Copy button, expand/collapse for long queries
  - Integrated with verification metadata display
- [ ] 6.1.4 VerificationPanel component (shows SQL execution results)
  - Display: schema, row count, bytes scanned, sample rows (max 10)
  - Positioned below SQL code block
  - Color-coded status: green (verified), yellow (warning), red (failed)
- [ ] 6.1.5 Thumbs up/down feedback buttons on assistant messages
  - Send feedback to backend for LLM improvement
  - Collect optional text feedback on thumbs down

**Acceptance Criteria**:
- Example prompts clickable and populate input
- Dashboard preview renders live charts with backend data
- SQL preview shows all queries with syntax highlighting
- Verification panel displays execution metadata correctly

---

### 6.2 Backend Integration (Enhanced)
**Complexity**: Medium | **Files**: Updates to existing chat-client.ts

**Note**: Phase 1.5 established `/chat` SSE connection. This phase adds dashboard-specific message types and workflows.

- [ ] 6.2.1 Extend SSE event handling for dashboard creation events
  - `yaml_generated`: Backend sends YAML definition
  - `sql_verified`: Backend sends verification results (schema, sample, bytes)
  - `dashboard_preview_ready`: Signal frontend to render preview
- [ ] 6.2.2 POST /v1/chat/create-dashboard workflow
  - Send: user prompt + optional context (existing dashboard to modify)
  - Receive: SSE stream with YAML, verification, preview data
  - Parse YAML into in-memory dashboard model
- [ ] 6.2.3 Iterative refinement handling
  - User sends follow-up: "Make bars red" or "Add filter for date"
  - Backend updates YAML incrementally
  - Frontend re-renders preview with updated YAML
- [ ] 6.2.4 Error handling for LLM failures specific to dashboards
  - SQL verification failed: Show error, offer to retry with adjusted query
  - YAML invalid: Show validation errors, suggest fixes
  - BigQuery quota exceeded: Suggest reducing query scope

**Acceptance Criteria**:
- Dashboard creation workflow streams YAML + verification progressively
- Iterative refinement updates preview without full regeneration
- SQL verification errors show actionable remediation steps
- All errors handled gracefully (no crashes)

### 6.3 Dashboard Creation Flow (E2E UX)
**Complexity**: Complex | **Files**: `apps/web/app/new/page.tsx`, workflow orchestration

- [ ] 6.3.1 "New Dashboard" button in gallery → Opens `/new` page with chat interface
  - Full-screen chat layout (no dashboard preview initially)
  - Welcome message: "Describe the dashboard you'd like to create"
  - Example prompts displayed (6.1.1)
- [ ] 6.3.2 User prompt submission workflow
  - User types natural language description (e.g., "Show top products by revenue")
  - Frontend sends via `useChat().append()` to backend
  - Backend Universal AI SDK generates YAML via LLM
- [ ] 6.3.3 YAML generation display (progressive)
  - Assistant message shows "Generating dashboard..."
  - YAML appears progressively as SSE streams (6.2.1)
  - CodeBlock component displays YAML with syntax highlighting
- [ ] 6.3.4 SQL verification loop display
  - Backend executes SQL queries automatically
  - VerificationPanel shows results for each query (6.1.4)
  - Display: schema, row count, bytes scanned, sample rows (max 10)
  - Color-coded status per query (green verified, red failed)
- [ ] 6.3.5 Preview rendering from generated YAML
  - DashboardPreviewCard appears in chat (6.1.2)
  - Renders live charts with real data from backend
  - User sees full dashboard inline without leaving chat
- [ ] 6.3.6 Iterative refinement workflow
  - User sends follow-up: "Make bars red" or "Add date filter"
  - Backend updates YAML incrementally (not full regeneration)
  - Preview updates in real-time with new YAML
  - Chat history shows full conversation context
- [ ] 6.3.7 "Save Dashboard" button in preview card
  - Opens dialog: name, description (optional), tags
  - Submits to backend: `POST /v1/dashboards`
  - Backend persists YAML, returns slug
  - Frontend shows success toast with "View Dashboard" button
- [ ] 6.3.8 Redirect to /dash/[slug] after save
  - Automatic redirect after 2 seconds
  - Or user clicks "View Dashboard" immediately
  - Dashboard loads with all charts functional

**Acceptance Criteria**:
- Full dashboard creation workflow completes without leaving chat
- YAML streams progressively with verification results
- Preview renders with live data (not mock)
- Iterative refinement updates preview correctly
- Save workflow persists dashboard and redirects successfully

---

### 6.4 "Explain This" Feature (Contextual AI Help)
**Complexity**: Medium | **Files**: Chart kebab menu integration, context building

- [ ] 6.4.1 "Explain this" button in chart kebab menus (⋮)
  - Positioned in chart header dropdown
  - Icon: question mark or lightbulb (monotone)
- [ ] 6.4.2 Context pre-filling logic
  - Gather: chart SQL, YAML definition, table schema, verification metadata
  - Include: bytes scanned, freshness timestamp, row count
  - Format as structured JSON for backend
- [ ] 6.4.3 Assistant panel auto-opens with context
  - If collapsed, panel expands automatically
  - Context message appears: "I've loaded the details for [Chart Name]. What would you like to know?"
  - User can immediately ask follow-up questions
- [ ] 6.4.4 LLM explains query logic in natural language
  - Backend LLM receives context + user question
  - Responds with plain English explanation
  - Examples: "This query counts unique users who logged in during the last 30 days, grouped by region."
- [ ] 6.4.5 Follow-up questions supported
  - User asks: "Why is the count different from last month?"
  - LLM has full context, can provide specific answer
  - Chat history persists context across session

**Acceptance Criteria**:
- "Explain this" button opens assistant with chart context loaded
- LLM provides accurate natural language explanation of SQL
- Follow-up questions work correctly (context retained)
- Verification metadata included in explanations (e.g., "This query scanned 1.2 GB")

---

**Phase 6 Deliverables**:
- Dashboard-specific chat components (ExamplePrompts, DashboardPreviewCard, VerificationPanel)
- Full dashboard creation workflow from prompt to saved dashboard
- Iterative refinement with live preview updates
- "Explain this" contextual help for charts
- SQL verification display with sample data

**Phase 6 Dependencies**:
- Phase 1.5 completed (chat UI, streaming, session management)
- Backend `/chat/create-dashboard` endpoint functional
- Backend SQL verification API returns schema + sample + metadata
- Backend supports incremental YAML updates for refinement

**Phase 6 Success Criteria**:
- User can create dashboard entirely through natural language (no YAML editing)
- Preview shows live data, not mocks
- Iterative refinement updates preview correctly (3+ rounds tested)
- "Explain this" feature provides accurate, helpful explanations
- All workflows tested E2E with real backend

---

## Phase 7: Lineage Visualization
**Days 24-25**

### 7.1 Graph Rendering Library Integration
- [ ] 7.1.1 Install reactflow or cytoscape.js
- [ ] 7.1.2 Evaluate library: reactflow (preferred for simplicity)
- [ ] 7.1.3 Configure layout algorithm (hierarchical or force-directed)

### 7.2 Lineage Graph Components
- [ ] 7.2.1 LineageGraph container component
- [ ] 7.2.2 Custom node components (4 types: dashboard, chart, query, table)
- [ ] 7.2.3 Node styling: color-coded (blue, green, yellow, orange)
- [ ] 7.2.4 Edge rendering (directional arrows: contains, executes, reads_from)
- [ ] 7.2.5 Pan and zoom controls
- [ ] 7.2.6 Minimap (optional, for large graphs)
- [ ] 7.2.7 Layer toggles (checkboxes to show/hide node types)
- [ ] 7.2.8 Search input (filter/highlight nodes by name)

### 7.3 Node Interactions
- [ ] 7.3.1 Click node: select and show metadata panel
- [ ] 7.3.2 Double-click node: expand/collapse children (if nested)
- [ ] 7.3.3 Drag node: reposition (auto-layout adjusts)
- [ ] 7.3.4 Hover node: tooltip with basic info

### 7.4 Metadata Panel
- [ ] 7.4.1 MetadataPanel component (right sidebar, 320px)
- [ ] 7.4.2 Display node name, type, ID
- [ ] 7.4.3 Query node: SQL preview, bytes scanned, execution time
- [ ] 7.4.4 Table node: schema snippet, partition info, row count, last updated
- [ ] 7.4.5 Chart node: chart type, query reference
- [ ] 7.4.6 Action buttons: "View SQL", "Explain", "Open in Builder"

### 7.5 Lineage Page (/lineage/[slug])
- [ ] 7.5.1 Lineage page layout (app/lineage/[slug]/page.tsx)
- [ ] 7.5.2 useLineage hook data fetching
- [ ] 7.5.3 Graph rendering from backend JSON (nodes + edges)
- [ ] 7.5.4 Loading state (skeleton graph or spinner)
- [ ] 7.5.5 Error state (missing lineage data)
- [ ] 7.5.6 Refresh button (re-fetch from backend)
- [ ] 7.5.7 Breadcrumb navigation to parent dashboard

**Phase 7 Acceptance Criteria**:
- Lineage graph loads and displays all nodes and edges
- Click node shows metadata panel with correct info
- Search filters and highlights nodes
- Layer toggles show/hide node types correctly
- "Open in Builder" navigates to /edit/[slug] with chart focused
- "Explain" opens Assistant with node context

---

## Phase 8: Additional Pages & Features
**Days 26-28**

### 8.1 Datasets Explorer Page (/datasets)
- [ ] 8.1.1 Three-panel layout: tree | schema | preview
- [ ] 8.1.2 BigQuery dataset tree (projects > datasets > tables)
- [ ] 8.1.3 Collapsible folders with expand/collapse icons
- [ ] 8.1.4 Table selection handler
- [ ] 8.1.5 Schema display: columns (name, type), partitioning, clustering
- [ ] 8.1.6 Data preview: first 100 rows (read-only table)
- [ ] 8.1.7 "Load More" button (fetch next page, max 500 rows)
- [ ] 8.1.8 Column name click: copy to clipboard
- [ ] 8.1.9 Search input: filter tree by table name
- [ ] 8.1.10 Refresh button: reload metadata from BigQuery
- [ ] 8.1.11 Backend integration: GET /v1/datasets, GET /v1/datasets/{table}/schema, GET /v1/datasets/{table}/preview

### 8.2 Settings Page (/settings)
- [ ] 8.2.1 Settings page layout with tab navigation
- [ ] 8.2.2 Appearance tab: Theme (Light/Dark/System), Density (Comfortable/Compact)
- [ ] 8.2.3 Preferences tab: Default view type, Date format, Time zone, Number format
- [ ] 8.2.4 Account tab: Email, Organization, Role (read-only), Sign Out button
- [ ] 8.2.5 Settings state (Zustand store or React Context)
- [ ] 8.2.6 Save button (POST /v1/settings)
- [ ] 8.2.7 Settings persistence and reload on save
- [ ] 8.2.8 Theme change immediate UI update

### 8.3 Help Page (/help)
- [ ] 8.3.1 Help page layout with searchable content
- [ ] 8.3.2 Keyboard shortcuts table (Navigation, Editor, Dashboard View)
- [ ] 8.3.3 Topic sections: Dashboards, Charts, Editor, Lineage
- [ ] 8.3.4 Collapsible accordion for topics
- [ ] 8.3.5 Search input: filter help topics
- [ ] 8.3.6 Markdown content rendering

### 8.4 Command Palette (Global)
- [ ] 8.4.1 Command palette component (Cmd/Ctrl+K)
- [ ] 8.4.2 Dashboard quick search (fuzzy match)
- [ ] 8.4.3 Recent dashboards list
- [ ] 8.4.4 Quick actions: New Dashboard, Settings, Help, Sign Out
- [ ] 8.4.5 Keyboard navigation (arrow keys, Enter to select)

**Phase 8 Acceptance Criteria**:
- Datasets explorer browses BigQuery schema correctly
- Table selection shows schema and data preview
- Settings page persists user preferences
- Theme changes apply immediately
- Help page displays keyboard shortcuts and topics
- Command palette opens with Cmd/Ctrl+K and allows quick navigation

---

## Phase 9: State Management & Error Handling
**Days 29-30**

### 9.1 Zustand Global Store
- [ ] 9.1.1 Create store/appStore.ts with TypeScript types
- [ ] 9.1.2 Dashboard state slice: current YAML model, dirty flag, last save timestamp
- [ ] 9.1.3 Assistant state slice: messages, conversation ID, loading state
- [ ] 9.1.4 UI state slice: sidebar collapsed, active tab, theme preference
- [ ] 9.1.5 Settings state slice: user preferences (view type, date format, etc.)
- [ ] 9.1.6 SessionStorage persistence middleware (optional, for editor state)
- [ ] 9.1.7 Autosave middleware (trigger save every 30s if dirty)

### 9.2 Error Boundaries & Handling
- [ ] 9.2.1 Global ErrorBoundary (wraps entire app)
- [ ] 9.2.2 Route-level error boundaries (per page)
- [ ] 9.2.3 Component-level error boundaries (charts, editor)
- [ ] 9.2.4 Error classification (lib/error-handling.ts): network, auth, validation, quota, server, client
- [ ] 9.2.5 Error display with trace IDs (from backend response headers)
- [ ] 9.2.6 Retry mechanisms: manual retry button, auto-retry with backoff
- [ ] 9.2.7 401 Unauthorized: redirect to /login
- [ ] 9.2.8 429 Rate Limit: show budget warning banner
- [ ] 9.2.9 500 Server Error: show friendly message with report link

### 9.3 Accessibility (WCAG AA Compliance)
- [ ] 9.3.1 Keyboard navigation: Tab, Enter, Esc work everywhere
- [ ] 9.3.2 Focus indicators: 2px solid ring on all interactive elements
- [ ] 9.3.3 ARIA labels on charts (role="img", descriptive aria-label)
- [ ] 9.3.4 Semantic HTML: proper heading hierarchy (h1, h2, h3)
- [ ] 9.3.5 Screen reader testing (NVDA, JAWS, VoiceOver)
- [ ] 9.3.6 Color contrast: 4.5:1 for normal text, 3:1 for large text
- [ ] 9.3.7 200% zoom test: usable without loss of functionality
- [ ] 9.3.8 prefers-reduced-motion: disable animations when set
- [ ] 9.3.9 Alt text for images and icons

### 9.4 Responsive Design
- [ ] 9.4.1 Mobile (<640px): single column, stacked layout
- [ ] 9.4.2 Tablet (640-1024px): 2-3 columns, collapsed sidebar
- [ ] 9.4.3 Desktop (>1024px): full 12-column grid, persistent sidebars
- [ ] 9.4.4 Touch targets: min 44x44px for mobile
- [ ] 9.4.5 Breakpoint testing: 320px, 640px, 768px, 1024px, 1440px

**Phase 9 Acceptance Criteria**:
- Global store manages dashboard, assistant, UI, settings state
- Autosave triggers every 30s when dirty
- Error boundaries catch and display errors gracefully
- All interactive elements keyboard-navigable
- WCAG AA compliance verified with automated tools
- Responsive layout works on mobile, tablet, desktop

---

## Phase 10: Testing
**Days 31-34**

### 10.1 Unit Tests (Vitest + React Testing Library)
- [ ] 10.1.1 Vitest setup and configuration
- [ ] 10.1.2 Chart component tests (LineChart, BarChart, AreaChart, TableChart, KPITile)
- [ ] 10.1.3 Dashboard widget tests (DashboardCard, FreshnessIndicator, FilterPanel)
- [ ] 10.1.4 Editor component tests (BuilderTab, YamlTab, PreviewTab, PropertiesPanel)
- [ ] 10.1.5 Utility tests (yaml-parser, error-handling, formatters)
- [ ] 10.1.6 Hook tests (useDashboards, useDashboard, useDashboardData, useLineage, useChat)
- [ ] 10.1.7 Coverage target: >80% for critical paths

### 10.2 E2E Tests (Playwright)
- [ ] 10.2.1 Playwright setup and configuration
- [ ] 10.2.2 E2E: Authentication flow (login, logout, session persistence)
- [ ] 10.2.3 E2E: Dashboard gallery (search, filter, navigate)
- [ ] 10.2.4 E2E: Dashboard view (render charts, freshness, filters)
- [ ] 10.2.5 E2E: Editor workflow (Builder → YAML → Preview → Save)
- [ ] 10.2.6 E2E: Chat creation (prompt → generate → preview → save)
- [ ] 10.2.7 E2E: Lineage view (graph render, node click, metadata)
- [ ] 10.2.8 E2E: Error scenarios (401, 404, 500, network errors)
- [ ] 10.2.9 CI configuration (GitHub Actions)

### 10.3 Performance Testing
- [ ] 10.3.1 Lighthouse audits (>90 performance, >95 accessibility)
- [ ] 10.3.2 Time to Interactive (TTI) <3s on cold cache
- [ ] 10.3.3 Chart render time <200ms (measured with React DevTools Profiler)
- [ ] 10.3.4 Bundle size: main <200KB gzipped, additional <150KB
- [ ] 10.3.5 Code splitting verification (route-based chunks)
- [ ] 10.3.6 Bundle analyzer report (webpack-bundle-analyzer or similar)
- [ ] 10.3.7 Performance budgets in CI (fail build if exceeded) _(Notes: Enforce Lighthouse ≥90, TBT <300ms, bundle ≤200KB per Frontend PDR §11)_

**Phase 10 Acceptance Criteria**:
- >80% test coverage for critical components
- All E2E user journeys pass consistently
- Lighthouse performance score >90
- Bundle size under budget (<200KB main)
- CI pipeline runs tests on every PR

---

## Phase 11: Deployment & Documentation
**Days 35-37**

### 11.1 Production Configuration
- [ ] 11.1.1 .env.production with production API URL
- [ ] 11.1.2 CSP headers configuration (Content-Security-Policy)
- [ ] 11.1.3 Gzip compression enabled (Next.js config)
- [ ] 11.1.4 Image optimization (next/image with remote patterns)
- [ ] 11.1.5 Sitemap generation (optional)
- [ ] 11.1.6 robots.txt configuration

### 11.2 Docker & Cloud Run Deployment
- [ ] 11.2.1 Dockerfile for apps/web (multi-stage build)
- [ ] 11.2.2 .dockerignore configuration
- [ ] 11.2.3 Cloud Run deployment config (YAML or Terraform)
- [ ] 11.2.4 Domain configuration and SSL certificate
- [ ] 11.2.5 Environment variable injection (Cloud Run secrets)
- [ ] 11.2.6 Health check endpoint (/api/health)
- [ ] 11.2.7 Deployment script (deploy.sh or Makefile target)

### 11.3 Monitoring & Observability
- [ ] 11.3.1 RUM (Real User Monitoring) integration (Cloud Monitoring, Vercel Analytics, or PostHog)
- [ ] 11.3.2 Error tracking (Sentry or Cloud Error Reporting)
- [ ] 11.3.3 Performance dashboards (Core Web Vitals)
- [ ] 11.3.4 Alerting rules (error rate >5%, p95 latency >3s)
- [ ] 11.3.5 Production E2E smoke tests (post-deployment)

### 11.4 Documentation
- [ ] 11.4.1 apps/web/README.md (setup, development, deployment)
- [ ] 11.4.2 Component documentation (TSDoc comments)
- [ ] 11.4.3 Dev workflow guide (how to add a new chart type, page, etc.)
- [ ] 11.4.4 Troubleshooting guide (common errors, solutions)
- [ ] 11.4.5 API integration guide (how frontend uses backend endpoints)

**Phase 11 Acceptance Criteria**:
- Frontend deployed to Cloud Run successfully
- Domain accessible with SSL
- RUM and error tracking operational
- Documentation complete and up-to-date
- Smoke tests pass in production

---

## Phase 12: MVP Validation & Demo
**Days 38-40**

### 12.1 Reference Dashboards
- [ ] 12.1.1 Create Dashboard 1: Revenue Analytics (Analytical view)
- [ ] 12.1.2 Create Dashboard 2: Operations KPIs (Operational view)
- [ ] 12.1.3 Verify all chart types render correctly (line, bar, area, table, kpi)
- [ ] 12.1.4 Test freshness indicators (mock stale data scenarios)
- [ ] 12.1.5 Test editor E2E (Builder → YAML → Preview → Save)
- [ ] 12.1.6 Test lineage view for both dashboards

### 12.2 MVP Feature Checklist (18 Features from PDR §11)
- [ ] 12.2.1 ✅ User can authenticate via Google SSO
- [ ] 12.2.2 ✅ Dashboard list displays all available dashboards
- [ ] 12.2.3 ✅ Dashboard view renders all charts from backend data
- [ ] 12.2.4 ✅ Each chart displays as-of timestamp and freshness indicator
- [ ] 12.2.5 ✅ User can initiate new dashboard via chat
- [ ] 12.2.6 ✅ Assistant generates YAML and displays preview
- [ ] 12.2.7 ✅ User can save dashboard and it persists
- [ ] 12.2.8 ✅ Edit mode allows color changes via UI
- [ ] 12.2.9 ✅ UI changes reflect in YAML model
- [ ] 12.2.10 ✅ YAML editor allows direct text editing
- [ ] 12.2.11 ✅ Save workflow shows dirty state indicator
- [ ] 12.2.12 ✅ Lineage view displays graph of dashboard composition
- [ ] 12.2.13 ✅ Dashboard loads in <3s on cold cache
- [ ] 12.2.14 ✅ Cached dashboard renders in <500ms
- [ ] 12.2.15 ✅ Individual chart renders in <200ms
- [ ] 12.2.16 ✅ Main bundle <200KB gzipped
- [ ] 12.2.17 ✅ Keyboard navigation works throughout app
- [ ] 12.2.18 ✅ WCAG AA compliance verified

### 12.3 Demo Preparation
- [ ] 12.3.1 Demo script (step-by-step walkthrough)
- [ ] 12.3.2 Demo fixtures (sample dashboards, queries, data)
- [ ] 12.3.3 Demo video (5-10min screencast)
- [ ] 12.3.4 Presentation slides (architecture, features, roadmap)

### 12.4 Internal Testing
- [ ] 12.4.1 Recruit ~10 internal users for testing
- [ ] 12.4.2 User testing sessions (observe, take notes)
- [ ] 12.4.3 Feedback collection form (Google Form or Typeform)
- [ ] 12.4.4 Bug triage and priority (P0, P1, P2)
- [ ] 12.4.5 Hotfix deployment for critical bugs

**Phase 12 Acceptance Criteria**:
- All 18 MVP features functional
- 2 reference dashboards created and verified
- Demo video and presentation ready
- Internal testing complete with feedback documented
- Critical bugs fixed before launch

---

## Timeline Summary

**Total Duration**: 40 days (~8 weeks)
**Developers**: 1-2 frontend engineers full-time

| Phase | Days | Status |
|-------|------|--------|
| Phase 1: Foundation & Setup | 3 | ✅ COMPLETE |
| Phase 2: OpenAPI Client & Auth | 3 | ✅ COMPLETE |
| Phase 3: Charts & Widgets | 6 | 🚧 50% (3.1 done, 3.2 pending) |
| Phase 4: Dashboard Pages & Data | 4 | ⏳ Pending |
| Phase 5: YAML Editor & Editing | 4 | ⏳ Pending |
| Phase 6: LLM Chat Assistant | 3 | ⏳ Pending |
| Phase 7: Lineage Visualization | 2 | ⏳ Pending |
| Phase 8: Additional Pages | 3 | ⏳ Pending |
| Phase 9: State & Error Handling | 2 | ⏳ Pending |
| Phase 10: Testing | 4 | ⏳ Pending |
| Phase 11: Deployment & Docs | 3 | ⏳ Pending |
| Phase 12: MVP Validation | 3 | ⏳ Pending |

**Next Milestone**: Phase 3.2 completion (Dashboard Widgets)
**Last Updated**: 2025-10-30
**Current Sprint**: Phase 3.2 - Dashboard Widget Components
