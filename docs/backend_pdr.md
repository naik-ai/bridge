# **Dashboard Platform — Product Design Reviews**

**Name**: Peter (after Peter Lynch)  
**Version**: 1.0 MVP  
**Date**: 2025-10-30  
**Owner**: Jay (Architect)  

---

## **PDR — Backend (MVP)**

### **1. Problem & Goals (MVP)**

**Problem**  
Build a fast, reliable data serving layer that pushes all heavy computation to BigQuery while enabling LLM-assisted dashboard authoring and verification. Current challenges include lack of versioned dashboard definitions, no observability into query lineage, and brittle manual SQL authoring without verification loops.

**Goals**  
- Serve compact, cache-first results to frontend with sub-second latency on repeated requests
- Enable LLM agents to propose, verify, and iterate on SQL queries through a structured backend verification loop
- Establish dashboards-as-code pattern with versioned YAML definitions as source of truth
- Provide minimal but sufficient auth and session management for single-tenant deployment
- Build lineage tracking from source tables through queries to dashboard visualizations
- Deploy observability scaffolding for query performance, cost tracking, and system health

### **2. Scope & Non-Goals (MVP)**

**In Scope**  
- REST API for dashboard lifecycle: validate, compile, save, serve data
- SQL execution service with verification loop: run queries, return metadata and small samples
- Manual precompute endpoint to warm cache on demand
- Lightweight Postgres for users, sessions, and dashboard indices
- Google SSO authentication with email allowlist
- OpenTelemetry instrumentation for critical paths
- YAML storage strategy decision point with basic versioning
- BigQuery query guardrails: result cache enforcement, byte scanning caps

**Out of Scope**  
- Automated scheduling or event-driven precompute workflows
- Client-side data joins or local computation beyond JSON serialization
- Multi-tenant isolation or advanced authorization
- Real-time collaborative editing
- Complex workflow orchestration beyond single-request processing
- Production-grade caching infrastructure beyond in-process or basic Redis

### **3. Architecture Overview**

**Core Components**

**API Service (FastAPI on Cloud Run)**  
Single service handling all backend operations. Exposes REST endpoints for dashboard management, SQL verification, data serving, and precompute triggering. Stateless except for cache access. Auto-scales based on request volume. Connects to BigQuery via service account credentials from Secret Manager.

**BigQuery Data Warehouse**  
All analytical queries execute here. Tables use partitioning and clustering for performance. Materialized views handle frequently-accessed aggregations. Result Cache is always enabled to minimize costs. Storage Read API used for large result sets. Projects follow multi-dataset pattern: raw, staging, mart layers.

**Cache Layer**  
MVP starts with in-process cache (Python dictionary or simple LRU). Optional Redis instance if performance demands. Cache keys include dashboard slug, query hash, and version identifier. Time-to-live acts as safety net. Cache population happens explicitly via precompute endpoint.

**Postgres Database (Minimal)**
Stores operational metadata only. Users and sessions for authentication. Prompt and action registry for future LLM context. Lineage graph nodes and edges (derived from YAML, can be rebuilt). Not used for dashboard content itself. YAML files are the single source of truth for all dashboard definitions.

**YAML Storage**
Two options under evaluation: Git repository (monorepo with dashboards folder) or GCS bucket with versioning. Git provides native version control and code review workflows. GCS offers simpler deployment and object versioning. YAML files are directly accessed by slug (filename = slug.yaml). Optional generated index file (.index.json) provides fast listing without DB queries or filesystem scanning.

**Secrets and Configuration**  
Secret Manager holds BigQuery service account keys, database credentials, OAuth secrets. Environment-specific config via Cloud Run environment variables or mounted config files.

**Component Interactions**
Frontend requests flow to API service. API service authenticates via session token lookup in Postgres. Dashboard content requests check cache first, fall back to BigQuery execution. SQL verification requests execute immediately on BigQuery with guardrails. Save operations write YAML to storage (single write, no DB sync needed). Lineage queries read from Postgres graph tables built from YAML during compile phase.

### **4. Data & Control Flows**

**Dashboard Authoring Flow (LLM-Assisted)**
User initiates dashboard creation through frontend chat interface. Frontend sends natural language prompt to API. API orchestrates LLM agent which generates initial YAML structure. Agent proposes SQL queries for each visualization. API receives SQL from agent, validates syntax, executes on BigQuery with strict byte limits. BigQuery returns full result set but API filters to metadata plus sample rows (maximum 100). API sends summary back to agent: column types, row counts, min/max values, sample data. Agent verifies logic, iterates if needed, finalizes YAML. API saves YAML to storage, builds lineage graph (derived from YAML). API returns success with dashboard slug to frontend.

**SQL Verification Loop Detail**  
Agent generates SQL statement. API wraps in execution context: sets query cache enabled, maximum bytes billed cap, execution timeout. BigQuery processes query using Result Cache if available. API receives complete result but transforms before returning to agent: extract schema, calculate statistics, sample up to 100 rows, record bytes scanned and duration. Agent receives verification payload, not raw data. Agent decides: accept and proceed, or revise SQL and retry. Loop continues until agent confirms or error limit reached.

**Dashboard Data Serving Flow**
Frontend requests dashboard via slug identifier. API checks session validity, loads YAML directly from filesystem (no DB query needed). API determines if cache contains fresh results using key pattern. On cache hit: serialize and return immediately. On cache miss: compile YAML to execution plan, execute queries in parallel on BigQuery, transform results to compact chart payloads, store in cache with version marker, return to frontend. Frontend receives object keyed by chart identifiers containing only necessary data points.

**Precompute Flow**  
Operator or script invokes precompute endpoint with dashboard slug. API loads dashboard YAML, compiles queries, executes all queries on BigQuery in parallel. API transforms each result to chart payload format, stores in cache with fresh version identifier. API updates dashboard metadata with new as-of timestamp. Subsequent frontend requests hit warm cache until TTL expires or manual invalidation.

### **5. Caching & Freshness Model**

**Cache Strategy**  
Explicit precompute model for MVP. No automatic refresh. Cache keys follow pattern: dashboard slug, query hash derived from SQL and parameters, version number from last save. Multiple queries in single dashboard cached independently. Cache stores serialized JSON payloads ready for frontend consumption.

**Freshness Semantics**  
Each cached result tagged with BigQuery execution timestamp. Precompute operation bumps version for entire dashboard. Frontend receives as-of timestamp with each chart payload. Users see staleness explicitly in UI. No background refresh in MVP.

**Cache Population**  
Manual trigger: operator calls precompute endpoint before users need data. On-demand: first uncached request executes and populates cache for subsequent users. Precompute preferred for consistent first-user experience.

**TTL and Eviction**  
Conservative TTL set as safety: 24-48 hours typical. Prevents unbounded growth. Version changes invalidate older cache entries implicitly. Manual purge endpoint available for troubleshooting.

**Future Evolution Path**  
Phase 1 introduces Pub/Sub event subscription. ETL pipeline completion triggers precompute automatically. Promotes cache from in-process to Redis/Memorystore for shared state across API instances. Phase 2 adds fine-grained invalidation based on query dependencies and upstream table changes.

### **6. Security & Access**

**Authentication**  
Google OAuth 2.0 flow for user login. Redirect to Google, verify token, extract email. Check email against allowlist stored in Secret Manager or config. Reject unknown users immediately. Create session record in Postgres with expiration timestamp. Issue session token to frontend as HTTP-only cookie.

**Authorization**  
MVP uses coarse-grained all-or-nothing model. Authenticated users have full access to all dashboards. Owner field in dashboard metadata tracks creator but doesn't enforce access control. Future phases introduce role-based access and row-level security.

**Service-to-Service Security**  
API service runs with dedicated service account. Least-privilege IAM roles: BigQuery Data Viewer, BigQuery Job User, Secret Manager Accessor, Cloud SQL Client. No user credentials stored in backend. All secrets retrieved from Secret Manager at startup or per-request.

**Network Security**  
Cloud Run enforces HTTPS. Internal Cloud SQL connection via private VPC or Cloud SQL Proxy. BigQuery accessed via Google Cloud APIs with service account authentication. No public database endpoints.

**Data Protection**  
No encryption at rest beyond Google Cloud defaults (all encrypted automatically). No PII or sensitive data expected in dashboard definitions. Future: customer-managed encryption keys if compliance demands.

### **7. Observability & Lineage**

**OpenTelemetry Instrumentation**  
Spans emitted for: dashboard compilation, SQL execution, data serving, cache operations, precompute jobs. Each span tagged with: dashboard slug, chart identifier, query hash, user identifier, execution duration, bytes scanned, row count, cache hit/miss status. Traces exported to Cloud Trace for visualization. Metrics exported to Cloud Monitoring for alerting.

**Logging Strategy**  
Structured JSON logs via Python logging to stdout. Cloud Run captures and indexes in Cloud Logging. Log levels: ERROR for failures, WARN for guardrail hits or performance degradation, INFO for major operations, DEBUG for development only. Include correlation IDs for request tracing.

**Lineage Tracking**  
Lineage graph built during dashboard compilation. Nodes represent: dashboards, charts, queries, BigQuery tables, BigQuery views, BigQuery materialized views. Edges represent: dashboard contains chart, chart executes query, query reads from table. Stored as simple node and edge tables in Postgres. API endpoint exposes graph in JSON format for frontend consumption. Future: parse SQL to extract column-level lineage, integrate with dbt metadata.

**Cost Monitoring**  
Every BigQuery execution logs bytes scanned. API enforces maximum_bytes_billed parameter on all queries. Exceeding limit fails fast before expensive execution. Daily rollup job aggregates bytes scanned by dashboard, user, query to identify cost hotspots. Alerts trigger on cost thresholds.

### **8. User Journeys**

**Journey 1: LLM-Assisted Dashboard Creation**  
Data analyst opens frontend, clicks "New Dashboard," enters natural language description: "Show me revenue trends by region for last 90 days." Backend receives request, orchestrates LLM agent which drafts YAML structure and proposes SQL queries. Agent sends SQL to backend verification endpoint. Backend executes on BigQuery, returns metadata: 3 columns (date, region, revenue), 270 rows, date range confirms last 90 days. Agent validates correctness, completes YAML. Backend saves to storage, builds lineage entries, returns dashboard slug to frontend. Frontend redirects to dashboard view showing rendered charts with fresh data.

**Journey 2: Manual SQL Verification Loop**  
LLM agent generates complex SQL with multiple CTEs. Agent calls verification endpoint. Backend executes on BigQuery but query returns zero rows due to logic error in join condition. Backend returns metadata showing 0 rows, sample empty. Agent detects issue, revises SQL to fix join. Agent retries verification endpoint. Backend executes revised SQL, returns metadata showing 15,000 rows and sample data. Agent confirms correctness, incorporates into YAML.

**Journey 3: Serving Compact Results**  
User navigates to existing dashboard. Frontend requests data via dashboard slug. Backend checks cache, finds miss. Backend loads YAML, compiles to execution plan identifying 5 queries. Backend executes all 5 in parallel on BigQuery. BigQuery returns result sets totaling 50,000 rows across queries. Backend transforms to compact payloads: time series becomes arrays of [timestamp, value] pairs; dimension tables become simple key-value maps. Backend stores in cache, returns to frontend. Total payload size: 250KB instead of 2MB raw data. Frontend renders in under 500ms.

**Journey 4: Manual Precompute**  
Operations engineer knows ETL completes at 6 AM daily. Engineer triggers precompute for critical executive dashboard at 6:15 AM. Backend loads dashboard YAML, compiles queries, executes on BigQuery. All queries hit fresh materialized views refreshed by ETL. Backend caches results with new version and current timestamp. First executive user at 7 AM receives instant response from warm cache.

### **9. Performance & Cost Guardrails**

**BigQuery Pushdown**  
Zero client-side computation on large datasets. All aggregation, filtering, joining, windowing happens in BigQuery. Frontend receives only visualization-ready data. Example: time series of 100 points, not 10,000 raw rows.

**Query Caps**  
Every query includes maximum_bytes_billed parameter set to 100 MB for MVP. Queries exceeding limit fail immediately. Alert fires for investigation. Prevents accidental full table scans or Cartesian joins from runaway costs. Limit adjustable per query via YAML configuration if needed.

**Result Cache Enforcement**  
All queries explicitly enable useQueryCache parameter. Repeated identical queries return in milliseconds at zero cost. Critical for developer iteration and dashboard refresh scenarios.

**Compact Payload Design**  
Backend never returns raw query results to frontend. Always transforms: select relevant columns only, sample rows if exceeding threshold, format timestamps as ISO strings not verbose objects, omit metadata fields not needed for visualization. Target: no single chart payload exceeds 100 KB.

**Performance Targets**  
Dashboard load from warm cache: p95 under 300ms. Dashboard load from cold (cache miss): p95 under 1.5 seconds. SQL verification endpoint: p95 under 2 seconds for queries scanning under 1 GB.

**Cost Visibility**  
Every API response includes bytes_scanned field. Frontend displays to power users for awareness. Weekly report aggregates total bytes scanned per dashboard to identify optimization opportunities. Budgets set at dashboard level for alerts.

### **10. Risks & Mitigations**

**Risk 1: File System Performance at Scale**
YAML files accessed directly from filesystem. For deployments with 1000+ dashboards, listing operations may degrade without optimization.
**Mitigation**: Implement optional generated index (.index.json) for O(1) listing. Use Cloud Run with mounted volumes or GCS FUSE for persistent storage. Consider caching list results in Redis with short TTL (5 minutes). Index regenerated on dashboard save/delete and server startup.

**Risk 2: LLM Generates Malicious or Expensive SQL**  
Agent produces SQL with unbounded scans, DROP statements, or attempts to access unauthorized datasets.  
**Mitigation**: Backend parses SQL before execution to detect dangerous patterns. Enforce maximum_bytes_billed cap on all executions. Service account has read-only permissions, cannot modify schema. Additional allowlist of permitted datasets.

**Risk 3: Cache Stampede on Popular Dashboard**  
Cache expires or invalidates during high traffic. Hundreds of concurrent requests hit BigQuery simultaneously.  
**Mitigation**: Implement request coalescing: first request executes, subsequent requests wait and share result. Alternatively, background refresh triggered at 80% of TTL prevents full expiration. Precompute critical dashboards explicitly before peak hours.

**Risk 4: BigQuery Quota Exhaustion**  
Aggressive query volume hits BigQuery API rate limits or concurrent query limits.  
**Mitigation**: Monitor Cloud Monitoring metrics for quota usage. Implement exponential backoff and retry logic. Set project-level reservations if predictable baseline load. Fail gracefully with clear error messages to users.

**Risk 5: Stale Data Surprises Users**  
Users unaware dashboard shows hours-old data, make decisions on outdated information.  
**Mitigation**: Prominent as-of timestamp in UI for every chart. Color coding: green for <1 hour old, yellow for 1-4 hours, red for older. API endpoint to check upstream table freshness and compare. Documentation sets expectations for refresh cadence.

### **11. Acceptance Criteria (MVP)**

**Functional Criteria**  
- Dashboard validate endpoint rejects invalid YAML with specific error messages
- Dashboard compile endpoint returns execution plan with query list and lineage seeds
- SQL run endpoint executes on BigQuery and returns metadata plus max 100 sample rows
- SQL run enforces maximum_bytes_billed cap and fails queries exceeding limit
- Dashboard save writes YAML to storage (single source of truth, no DB sync)
- Data serving endpoint returns cached results in under 300ms on repeat request
- Data serving endpoint executes queries on cache miss and populates cache
- Precompute endpoint warms cache for specified dashboard
- Lineage endpoint returns graph JSON for existing dashboard
- Auth flow validates Google SSO token and checks allowlist

**Performance Criteria**  
- Dashboard load from warm cache: p95 latency under 300ms
- Dashboard load from cold cache: p95 latency under 1.5 seconds
- SQL verification: p95 latency under 2 seconds for <1 GB scans
- API supports 100 concurrent requests without degradation

**Observability Criteria**  
- OpenTelemetry spans present for all critical operations
- Spans include minimum required attributes: slug, query_hash, duration, bytes_scanned
- Traces visible in Cloud Trace within 60 seconds of execution
- Logs structured JSON format with correlation IDs

**Demonstration Criteria**  
- Create two sample dashboards entirely through LLM chat interface
- Dashboards render successfully with real data from BigQuery
- Manual precompute reduces subsequent load time to under 300ms
- Lineage view shows connections from dashboard to source tables

### **12. Implementation Phasing**

**MVP Completion (Current Focus)**  
FastAPI service deployed to Cloud Run with all core endpoints operational. YAML validation and compilation logic functional. SQL execution with guardrails and sample limiting. Basic cache implementation. Minimal Postgres schema deployed. Google SSO with allowlist active. OpenTelemetry export to Cloud Trace. Two reference dashboards built and serving data. Target completion: Week 8.

**Phase 1 Preview (Post-MVP)**  
Event-driven precompute: Pub/Sub subscription to ETL completion events triggers automatic cache refresh. Upgrade cache infrastructure from in-process to Redis or Memorystore for multi-instance consistency. Deploy materialized views for hottest query paths. Lineage endpoint enhanced with richer metadata. Estimated timeline: Weeks 9-12.

**Phase 2/3 Preview (Future)**  
Fine-grained cache invalidation based on query dependency analysis. BI Engine enabled for most-accessed datasets to reduce latency below 200ms. External context ingestion: Slack threads and Linear issues stored in Postgres for LLM reference during dashboard creation. Advanced authorization with row-level security and authorized views. Custom chart types beyond standard library. Estimated timeline: Months 4-6.

### **12.1 Implementation Status & Task Trace (2025-10-31)**

| Area | Status | Task Reference | Notes |
|------|--------|----------------|-------|
| Foundation & Setup (Phase 1) | ✅ Complete | docs/task.md (Backend Phase 1) | SQLModel migrations, BigQuery guardrails, cache primitives landed with 19 tests passing; forms baseline for all later phases. |
| Services Layer (Phase 2) | ✅ Complete | docs/task.md (Phase 2.1-2.9) | Ten async services shipped; P0 async gaps resolved during Phase 2 sweep—unblocks verification loop and lineage. |
| API Endpoints (Phase 3) | ⚠️ Shipping w/ placeholder data | docs/task.md (Phase 3.1-3.7) | All 14 routes live; `GET /v1/data/{slug}` and `POST /v1/precompute` still return marked placeholder payloads (apps/api/src/services/data_serving.py, precompute.py) pending query execution wiring. |
| Schema Browser API | ✅ Complete | docs/task.md (Phase 4.1, Phase 8.1) | `/v1/schema/*` endpoints implemented with Redis caching (datasets 1h, tables 15m) and FREE BigQuery APIs; supports Dataset Explorer UX. |
| Guardrails Backlog | 🚧 In Progress | docs/task.md §2.10 | Dataset allowlist, SQL sanitiser, cache TTL/purge endpoint scheduled; required to close PDR §9 risk mitigations. |

**Outstanding follow-ups**
- Replace placeholder responses in DataServing/Precompute with real execution + cache writes before declaring PDR §5 complete.
- Implement guardrail backlog (SQL sanitiser, dataset allowlist, cache TTL/purge) to satisfy Risk 2 & Risk 3 mitigations.
- Wire bytes_scanned + latency metrics into every response/log per docs/task.md Phase 4.

### **12.2 Decision Log (Updated)**
- **YAML SSOT migration (2025-10-31)** — Dashboard definitions now stored exclusively in `/dashboards/*.yaml`; Postgres `dashboards` table deprecated. Rationale: eliminate drift, simplify deploy surface, improve developer ergonomics (git reviewable configs). Value: reduces 200–300 LoC, removes periodic sync job.
- **Schema Browser cost posture** — Adopted BigQuery `datasets.list` + `tabledata.list` APIs only (no billed query jobs). Ensures zero-cost browsing while meeting PDR §9 cost guardrails.
- **Async compliance sweep** — Converted blocking service methods to async/await (see docs/task.md Phase 2 deliverables). Keeps event loop free for chat + precompute workloads.

### **12.3 Schema Browser Implementation Snapshot**
- Endpoints: `/v1/schema/datasets`, `/v1/schema/datasets/{id}/tables`, `/v1/schema/tables/{id}/schema|metadata|preview`, `/v1/schema/cache/invalidate`.
- Caching: Dataset lists cached 1 hour; table schema & metadata cached 15 minutes; previews remain uncached to guarantee fresh data.
- Pagination: Cursor-based pagination defaults to 50 rows (configurable up to 1000) for table previews—aligned with UI Explorer v1.
- Safety: Never caches raw data; relies on BigQuery free metadata APIs; retries/backoff handled inside `SchemaService`.

### **13. Open Questions & Assumptions**

**Questions**  
- YAML storage rollout: Git-backed `/dashboards` directory adopted MVP (2025-10-31); revisit GCS option once multi-env deployment requires remote writes.
- Freshness SLA: what is acceptable staleness for different dashboard types? Need stakeholder input to set refresh cadence targets.
- BI Engine allocation: what budget and datasets should use BI Engine acceleration? Requires cost-benefit analysis.
- Multi-tenancy path: stay single-tenant or design for eventual multi-org? Impacts auth and data isolation decisions.

**Assumptions**  
- Single GCP project contains all resources for MVP
- Target user base: 100-1000 users, single organization
- Dashboard count: 50-500 dashboards, 5-20 queries each
- Query complexity: typical OLAP queries, no streaming or real-time requirements
- BigQuery datasets already exist with stable schemas and documented ETL
- Development team has GCP and Python expertise
- LLM provider API (Anthropic Claude) available and performant

---
