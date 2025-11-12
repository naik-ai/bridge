# Task Reorganization Plan - MVP-First Approach

## Executive Summary

**Problem**: Current Phase 0 includes 15+ tables and heavy onboarding services (doc crawl, PII, glossary, governance) that violate "Postgres as directory, GCS as data lake" and block MVP dashboard generation.

**Solution**: Minimize Phase 0 to team + connection validation only. Defer all artifact generation to post-Universal AI SDK phases. Prioritize dashboard YAML generation via chat.

---

## Current vs. Target Phase Structure

### Current Structure (Problematic)
```
Phase 0: Team Onboarding (15+ tables, doc/PII/glossary services) ❌
  ├─ 0.1: Database Models (lines 9-34) - 17 models including glossary, goals, policies
  ├─ 0.2: Infrastructure Setup (lines 36-51) - KMS, GCS, Secret Manager
  ├─ 0.3.1-0.3.15: Services (lines 53-325) - doc crawler, PII, glossary, governance
  └─ 0.4: API Endpoints (lines 327+)

Phase 1: Foundation (Backend basic setup)
Phase 2: Core Services
Phase 2.12: Universal AI SDK ✅ (added, ready)
Phase 3: API Endpoints
```

### Target Structure (MVP-First)
```
Phase 0: Minimal Onboarding (4 tables: teams, connections, datasets, tables) ✅
  ├─ Team + Connection setup only
  ├─ BigQuery validation (SELECT 1 dry-run)
  └─ Lightweight catalog scan (INFORMATION_SCHEMA only)

Phase 1: Foundation (Backend FastAPI + DB)
Phase 2: Core Services + GCS Storage Adapter
Phase 2.12: Universal AI SDK Infrastructure ✅ (already added)
Phase 3: Chat API Endpoints (session, streaming, messages)
Phase 3.5: Dashboard YAML Generation via LLM 🎯 NEW - MVP PRIORITY
Phase 4: Dashboard CRUD API
Phase 5: Dashboard View + Data Serving

DEFERRED TO POST-MVP:
Phase X: Advanced Onboarding (doc crawl, PII, glossary, governance)
Phase Y: Artifacts & Lineage
Phase Z: Observability & Cost Controls
```

---

## Detailed Reorganization

### **Phase 0: Minimal Onboarding** (Trimmed from 17 tables → 4 tables)

**Keep (4 tables)**:
- `Team` (id, name, slug, admin_user_id, created_at, updated_at)
- `Connection` (id, team_id, name, warehouse_type, credentials_gcs_path, status, validated_at)
- `Dataset` (id, connection_id, fully_qualified_name, description, location, last_modified)
- `Table` (id, dataset_id, fully_qualified_name, table_type, row_count, size_bytes)

**Defer to Phase X (Post-MVP)**:
- `Column` - defer until schema exploration needed
- `PIIDetection` - defer to governance phase
- `DbtArtifact` - defer to dbt integration
- `DocSource` - defer to doc crawler phase
- `GlossaryTerm` - defer to glossary extraction
- `BusinessGoal` - defer to goal mapping
- `DataPolicy` - defer to governance phase
- `OnboardingReport` - defer (replace with session-based onboarding in Universal AI SDK)
- `OnboardingJob` - defer (use SessionManifest for tracking instead)
- `WorkspacePreferences` - defer to post-MVP customization

**Services to Keep**:
- `ConnectionService` (create, validate, list)
- `CatalogService` (lightweight scan of datasets + tables only, no columns)
- `EncryptionService` (KMS for service account credentials)
- `StorageService` (GCS upload/download for service accounts)

**Services to Defer**:
- `PIIDetectorService` → Phase X
- `DbtService` → Phase X
- `DocCrawlerService` → Phase X
- `LLMService` (onboarding-specific) → Phase X (note: separate LLM service for chat exists in Universal AI SDK)
- `BusinessGoalsService` → Phase X
- `CostEstimatorService` → Phase X
- `ReportGeneratorService` → Phase X
- `GovernanceService` → Phase X

---

### **Phase 3.5: Dashboard YAML Generation via LLM** 🎯 NEW - INSERT AFTER PHASE 3

**Duration**: ~3 hours | **Priority**: CRITICAL - MVP BLOCKER

**Dependencies**: Phase 2.12 complete (Universal AI SDK), Phase 3 complete (Chat API)

#### 3.5.1 Dashboard Generation Tools (1 hour)
- [ ] Create `src/ai_sdk/tools/bigquery_tool.py` (registered with Universal AI SDK)
  - `async list_datasets(connection_id) -> List[dict]`
  - `async list_tables(dataset_name) -> List[dict]`
  - `async get_table_schema(table_name) -> dict`
  - `async run_dry_run_query(sql, max_bytes_billed=100_000_000) -> dict` (metadata only)

- [ ] Create `src/ai_sdk/tools/yaml_tool.py`
  - `async validate_dashboard_yaml(yaml_content) -> dict` (JSON Schema validation)
  - `async save_dashboard_yaml(yaml_content, slug, team_id) -> str` (GCS path)
  - `async list_dashboards(team_id) -> List[dict]`

#### 3.5.2 Dashboard Generation Prompt Blocks (30 minutes)
- [ ] Create `PromptBlock` records in DB:
  - **Block 1**: System prompt with YAML schema definition (cache-control: ephemeral)
  - **Block 2**: BigQuery best practices (partitioning, clustering, avoid SELECT *)
  - **Block 3**: Dashboard layout rules (12-column grid, view types, color monotone theme)

- [ ] Add to `PromptBlockService`:
  - `get_dashboard_generation_context() -> List[PromptBlock]`

#### 3.5.3 Dashboard Generation Agent Workflow (1 hour)
- [ ] Implement `DashboardGenerationService` (wraps Universal AI SDK Orchestrator)
  - `async generate_dashboard(session_id, user_message, connection_id) -> AsyncGenerator`
    1. Load prompt blocks (YAML schema, BigQuery best practices, layout rules)
    2. Load available datasets/tables from connection
    3. Call `orchestrator.send_message()` with tools: [bigquery_tool, yaml_tool]
    4. Stream SSE events: tool_call (list_tables), tool_result, token, yaml_artifact
    5. Agent iterates: explore schema → propose SQL → dry-run → validate → generate YAML
    6. On success: Save YAML to GCS + create Dashboard record in DB
    7. Return: {dashboard_slug, gcs_yaml_path, preview_url}

- [ ] Add acceptance criteria:
  - Agent MUST run dry-run query before finalizing SQL (verify bytes_scanned < 100 MB)
  - Agent MUST validate YAML against JSON Schema before saving
  - Agent SHOULD suggest partitioned queries when scanning >1 GB
  - Agent SHOULD use monotone color theme (neutral grey) by default

#### 3.5.4 Dashboard CRUD Integration (30 minutes)
- [ ] Create `Dashboard` model (SQLModel):
  - Fields: id, team_id, slug, title, description, gcs_yaml_path, owner_user_id, view_type, version, created_at, updated_at
  - Indexes: idx_team_dashboards, idx_dashboard_slug

- [ ] Add Alembic migration:
  - `alembic revision --autogenerate -m "Add Dashboard model"`

- [ ] Update `DashboardService`:
  - `async create_dashboard(team_id, slug, gcs_yaml_path) -> Dashboard`
  - `async get_dashboard(slug) -> Dashboard` (returns pointer, frontend fetches YAML from GCS)
  - `async list_dashboards(team_id) -> List[Dashboard]`

---

### **Phase 4: Dashboard Data Serving** (Update existing)

**Current**: Includes YAML validation, compilation, precompute
**Change**: Remove YAML storage logic (already handled by Phase 3.5), focus on query execution + cache

#### 4.1 Query Execution Service
- Keep: BigQuery client wrapper
- Keep: Result cache (Redis/in-process)
- Keep: Byte cap enforcement (max_bytes_billed)
- Keep: Compact payload transformation (BigQuery rows → chart JSON)

#### 4.2 Precompute Service
- Keep: Manual cache warming endpoint
- Add: Load YAML from GCS (not DB)

#### 4.3 Data Serving Endpoint
- `GET /v1/dashboards/{slug}/data`
  - Load Dashboard record from DB → get gcs_yaml_path
  - Fetch YAML from GCS
  - Compile queries
  - Execute with cache check
  - Return compact JSON

---

## Migration Path

### Step 1: Trim Phase 0 (Remove 13 tables + 11 services)
- [ ] Edit `docs/task.md` lines 9-325
- [ ] Move deferred tables to new "Phase X: Advanced Onboarding (Post-MVP)" section
- [ ] Mark deferred services with "⏸️ DEFERRED" status
- [ ] Keep only: Team, Connection, Dataset, Table models + 4 core services

### Step 2: Insert Phase 3.5 (Dashboard Generation)
- [ ] Add new section after Phase 3 (line ~980)
- [ ] 4 subsections: Tools, Prompt Blocks, Agent Workflow, CRUD Integration
- [ ] ~15 detailed tasks

### Step 3: Update Phase 4 (Dashboard Data Serving)
- [ ] Remove YAML storage tasks (already in Phase 3.5)
- [ ] Focus on query execution + cache
- [ ] Update dependencies: Requires Phase 3.5 complete

### Step 4: Create Phase X (Deferred Onboarding)
- [ ] New section at end of Backend tasks
- [ ] Contains all deferred Phase 0 work: doc crawl, PII, glossary, governance
- [ ] Mark as "Post-MVP - Requires cost guardrails + Universal AI SDK"

---

## Key Principles (Enforced)

1. **Postgres as Directory, GCS as Data Lake**
   - Dashboard YAML → GCS (`gs://bridge-dashboards/{team_id}/{slug}.yaml`)
   - Session logs → GCS (already in Phase 2.12)
   - Onboarding reports → GCS (when re-added in Phase X)
   - DB stores: pointers (gcs_yaml_path), metadata (slug, title, owner), summaries only

2. **MVP Priority: Dashboard Generation via Chat**
   - Universal AI SDK (Phase 2.12) → Chat API (Phase 3) → Dashboard Generation (Phase 3.5) → Data Serving (Phase 4)
   - Onboarding complexity deferred until this pipeline works end-to-end

3. **Cost Guardrails Before Heavy Jobs**
   - Phase 3.5 includes byte caps for dry-runs (100 MB default)
   - Background jobs (doc crawl, PII) deferred to Phase X when guardrails defined
   - Circuit breakers, rate limits, retry policies documented before enabling

4. **No Artifact Generation on the Fly (MVP)**
   - Glossary, goals, policies, lineage → deferred to Phase X/Y
   - Focus: user asks for dashboard → agent generates YAML → saves to GCS → done

---

## Updated Phase Durations (Rough Estimate)

| Phase | Duration | Status | Priority |
|-------|----------|--------|----------|
| Phase 0 (Minimal Onboarding) | ~4 hours | ⏳ Pending | High |
| Phase 1 (Foundation) | ~6 hours | ⏳ Pending | High |
| Phase 2 (Core Services + GCS) | ~8 hours | ⏳ Pending | High |
| Phase 2.12 (Universal AI SDK) | ~7 hours | ✅ Documented | **Critical** |
| Phase 3 (Chat API) | ~1.5 hours | ✅ Documented | **Critical** |
| **Phase 3.5 (Dashboard Gen)** | **~3 hours** | 📝 New | **CRITICAL - MVP BLOCKER** |
| Phase 4 (Data Serving) | ~4 hours | ⏳ Pending | High |
| Phase 5 (Observability) | ~3 hours | ⏳ Pending | Medium |
| Phase 6 (Deployment) | ~2 hours | ⏳ Pending | Medium |
| **Phase X (Advanced Onboarding)** | **~20 hours** | ⏸️ Deferred | Post-MVP |
| **Phase Y (Artifacts & Lineage)** | **~8 hours** | ⏸️ Deferred | Post-MVP |

**Total MVP Path**: ~35 hours (vs. 55+ hours with bloated Phase 0)

---

## Success Criteria

### Before Reorganization ❌
- Phase 0 blocks MVP for 2 weeks (doc crawl, PII, glossary)
- 15+ tables violate "Postgres as directory"
- No clear path from chat to dashboard YAML

### After Reorganization ✅
- Phase 0 completes in 4 hours (team + connection only)
- 4 tables in Phase 0, all pointers (GCS paths)
- Clear MVP path: Universal AI SDK → Chat → Dashboard Gen → Data Serving
- Heavy onboarding deferred until cost guardrails + foundation stable

---

## Next Steps

1. **Get approval** on this reorganization plan
2. **Execute Step 1**: Trim Phase 0 (remove 13 tables, defer 11 services)
3. **Execute Step 2**: Insert Phase 3.5 (Dashboard Generation)
4. **Execute Step 3**: Update Phase 4 (remove YAML storage logic)
5. **Execute Step 4**: Create Phase X (Deferred Onboarding) at end
6. **Update backend_pdr.md**: Add Phase 3.5 section, update Phase 0 scope
