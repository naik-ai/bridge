# **Dashboard Platform — Product Design Reviews**

**Name**: Peter (after Peter Lynch)
**Version**: 2.0 (Realigned with Universal AI SDK Architecture)
**Date**: 2025-11-03
**Owner**: Jay (Architect)

**📋 Implementation Tasks**: See `/docs/backend_tasks.md` for detailed, metadata-oriented task breakdown with dependencies and acceptance criteria.

---

## **PDR — Backend (MVP)**

### **⚠️ Reorganization Notice (2025-11-03)**

This PDR has been realigned per `/docs/system_alignment.md` to enforce:
1. **Postgres as Directory, GCS as Data Lake** - All long-form content (messages, YAML, artifacts) stored in GCS; Postgres stores pointers only
2. **Dashboard Generation via Chat is MVP Priority** - Universal AI SDK → Chat API → Dashboard YAML Generation → Data Serving
3. **No Artifact Generation on the Fly (MVP)** - Defer doc crawl, PII, glossary, governance to post-MVP Phase X
4. **Cost Guardrails Before Heavy Jobs** - Byte caps, rate limits, circuit breakers enforced before enabling background jobs

**Key Changes**:
- **Phase 0** trimmed from 17 tables → 4 tables (Team, Connection, Dataset, Table)
- **Phase 3.5** added: Dashboard YAML Generation via LLM (MVP blocker)
- **Phase X** created: Advanced Onboarding (doc crawl, PII, glossary) deferred to post-MVP
- See `/docs/task_reorganization_plan.md` for rationale and migration details

---

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

### **3.1 Universal AI SDK Architecture**

The backend includes a **Universal AI SDK** layer that provides a consistent interface for multi-provider LLM interactions. This is the core orchestrator for all agent-based features and chat-driven dashboard creation.

**Key Components**

**1. Abstract Orchestrator Interface** (`src/ai_sdk/orchestrator.py`)

Base class defining standard methods for LLM interactions:
- `create_session(user_id, model, tools) -> Session`: Initialize new chat session
- `send_message(session_id, content) -> AsyncGenerator`: Send message and stream response
- `execute_tool(tool_name, args) -> ToolResult`: Execute tool with deterministic caching
- `cache_prompt(block_name, content, cache_control)`: Register reusable prompt blocks
- Provider-agnostic types: `Session`, `Message`, `Artifact`, `ToolCall`, `PromptBlock`
- Async-first API with type safety throughout

**2. Provider Adapters** (`src/ai_sdk/providers/`)

Wrap provider-specific SDKs with universal interface:
- `ClaudeAgentAdapter`: Wraps Anthropic Claude SDK with Computer Use and Prompt Caching extensions
- `OpenAIAdapter`: Future integration with OpenAI Assistants API (planned)
- `GoogleAdapter`: Future integration with Google Vertex AI Agent Builder (planned)
- Each adapter translates universal types to provider-specific formats
- Handles provider-specific features (e.g., Anthropic cache-control headers)

**3. Session Management** (`src/ai_sdk/session.py`)

GCS-backed session storage with Postgres pointers:
- **Session Manifest**: JSON document in GCS with metadata and message log pointers
- **GCS Layout**:
  - `gs://bridge-sessions/{session_id}/manifest.json` → session metadata
  - `gs://bridge-sessions/{session_id}/messages-{chunk}.jsonl` → JSONL message logs
  - `gs://bridge-sessions/{session_id}/artifacts/{sha256}.bin` → deduplicated artifacts
- **Postgres Pointers**: `sessions` table stores only `session_id`, `user_id`, `gcs_path`, `status`, timestamps
- **No full message content in Postgres** → keeps DB lean, scales to long conversations

**4. Prompt Registry** (`src/ai_sdk/prompts.py`)

Centralized registry of reusable prompt blocks with cache-control metadata:
- Supports Anthropic cache-control directives (`ephemeral` for 5-minute cache, `static` for 24-hour cache)
- Versioned prompts with SHA-based cache key generation
- Example blocks: `system_prompt_dashboard_creation`, `context_budget_policy`, `safety_guardrails`
- Blocks loaded from `prompt_blocks` table at runtime
- Cache-control headers injected automatically for Anthropic provider

**5. Tool Orchestration** (`src/ai_sdk/tools.py`)

Tool execution with deterministic caching:
- Tool cache layer with key generation: `tool:{tool_name}:{args_hash}`
- Args hash computed via SHA-256 of canonicalized JSON (sorted keys)
- Cache stored in `tool_cache` table (metadata) + GCS (payload)
- Tool execution tracking in `tool_calls` table: session_id, tool_name, args, result, cached, duration_ms
- Result validation and type conversion
- TTL varies by tool type: short-lived (1 min) vs stable (24 hours)

**6. Cost Tracking** (`src/ai_sdk/metrics.py`)

Per-call token counting and cost calculation:
- Token counting: `input_tokens`, `output_tokens`, `cached_input_tokens` (from provider response)
- Cost calculation based on provider pricing tables:
  ```python
  # Example: Anthropic Claude Sonnet 4.5
  cost_usd = (
      (input_tokens - cached_input_tokens) * 0.003 / 1000 +  # Input @ $0.003/1K
      cached_input_tokens * 0.0003 / 1000 +                   # Cached input @ 90% discount
      output_tokens * 0.015 / 1000                            # Output @ $0.015/1K
  )
  ```
- Aggregation: per-session, per-user, per-model, per-time-window
- Budget enforcement: reject requests exceeding monthly budget threshold

**Storage Pattern**

```
GCS Bucket: gs://bridge-sessions/
├── {session_id}/
│   ├── manifest.json          # Session metadata + message pointers
│   ├── messages/
│   │   ├── messages-0001.jsonl    # JSONL append-only log (chunk 1)
│   │   └── messages-0002.jsonl    # JSONL append-only log (chunk 2)
│   └── artifacts/
│       ├── {sha256_1}.bin     # Deduplicated binary artifacts
│       └── {sha256_2}.bin

Postgres Tables:
- sessions: Pointers to GCS manifests (NOT full content)
  → Fields: session_id, user_id, gcs_path, provider, model, total_tokens, total_cost_usd, status
- model_calls: Log of all LLM API calls
  → Fields: session_id, provider, model, input_tokens, output_tokens, cached_input_tokens, cost_usd, latency_ms
- artifacts: Index with SHA for deduplication
  → Fields: session_id, content_sha256, gcs_uri, size_bytes, mime_type
- tool_cache: Deterministic cache for tool execution results
  → Fields: tool_name, cache_key, gcs_payload_uri, ttl_seconds, expires_at, hit_count
- prompt_blocks: Registry of reusable prompts with cache metadata
  → Fields: block_name, content, cache_control_type, version
```

**Why This Architecture?**

1. **GCS = Data Lake**: Cheap, durable storage for long conversations and large artifacts
2. **Postgres = Directory**: Fast metadata queries, no bloat from message content
3. **Provider Independence**: Easy to switch between Claude, GPT-4, Gemini without frontend changes
4. **Cost Optimization**: Anthropic prompt caching reduces costs by 90% on repeated context
5. **Deterministic Tool Caching**: Avoid redundant expensive operations (BigQuery queries, API calls)
6. **Scalability**: Sessions can grow to 1000+ messages without Postgres performance impact

### **4. Data & Control Flows**

**Dashboard Authoring Flow (LLM-Assisted)**
User initiates dashboard creation through frontend chat interface. Frontend sends natural language prompt to API. API orchestrates LLM agent which generates initial YAML structure. Agent proposes SQL queries for each visualization. API receives SQL from agent, validates syntax, executes on BigQuery with strict byte limits. BigQuery returns full result set but API filters to metadata plus sample rows (maximum 100). API sends summary back to agent: column types, row counts, min/max values, sample data. Agent verifies logic, iterates if needed, finalizes YAML. API saves YAML to storage, builds lineage graph (derived from YAML). API returns success with dashboard slug to frontend.

**SQL Verification Loop Detail**  
Agent generates SQL statement. API wraps in execution context: sets query cache enabled, maximum bytes billed cap, execution timeout. BigQuery processes query using Result Cache if available. API receives complete result but transforms before returning to agent: extract schema, calculate statistics, sample up to 100 rows, record bytes scanned and duration. Agent receives verification payload, not raw data. Agent decides: accept and proceed, or revise SQL and retry. Loop continues until agent confirms or error limit reached.

**Dashboard Data Serving Flow**
Frontend requests dashboard via slug identifier. API checks session validity, loads YAML directly from filesystem (no DB query needed). API determines if cache contains fresh results using key pattern. On cache hit: serialize and return immediately. On cache miss: compile YAML to execution plan, execute queries in parallel on BigQuery, transform results to compact chart payloads, store in cache with version marker, return to frontend. Frontend receives object keyed by chart identifiers containing only necessary data points.

**Precompute Flow**
Operator or script invokes precompute endpoint with dashboard slug. API loads dashboard YAML, compiles queries, executes all queries on BigQuery in parallel. API transforms each result to chart payload format, stores in cache with fresh version identifier. API updates dashboard metadata with new as-of timestamp. Subsequent frontend requests hit warm cache until TTL expires or manual invalidation.

### **4.1 Session Manifest Flow (Universal AI SDK)**

The **Session Manifest** is the core data structure for LLM interactions. It lives in GCS with Postgres pointers, enabling scalable multi-turn conversations.

**Flow: Create Session**

```
┌─────────────┐
│   User      │
│ (Chat UI)   │
└──────┬──────┘
       │ 1. Start new chat
       ▼
┌─────────────────────────────────────────────────────────────┐
│  POST /api/v1/sessions                                      │
│  ├─> SessionService.create_session(user_id, model, tools)   │
│  │   ├─> Generate session_id (UUID)                         │
│  │   ├─> Create GCS manifest:                               │
│  │   │   gs://bridge-sessions/{session_id}/manifest.json    │
│  │   │   {                                                   │
│  │   │     session_id, user_id, model, tools,               │
│  │   │     messages_uri: "gs://.../messages-0001.jsonl",    │
│  │   │     artifacts: [],                                   │
│  │   │     metadata: {created_at, updated_at}               │
│  │   │   }                                                   │
│  │   ├─> Insert pointer in Postgres:                        │
│  │   │   sessions(session_id, user_id, gcs_path, status)    │
│  │   └─> Return session_id                                  │
│  └─> Response: {session_id, gcs_path, provider, model}      │
└─────────────────────────────────────────────────────────────┘
```

**Flow: Send Message**

```
┌─────────────┐
│   User      │
│ (Chat UI)   │
└──────┬──────┘
       │ 2. Send message "Show me revenue for Q4"
       ▼
┌─────────────────────────────────────────────────────────────┐
│  POST /api/v1/chat (SSE streaming)                          │
│  ├─> SessionService.add_message(session_id, role, content)  │
│  │   ├─> Load manifest from GCS                             │
│  │   ├─> Generate message_id (UUID)                         │
│  │   ├─> Append message to JSONL:                           │
│  │   │   gs://.../messages-0001.jsonl                       │
│  │   │   {"id": "msg_123", "role": "user",                  │
│  │   │    "content": "Show me revenue for Q4",              │
│  │   │    "timestamp": "2025-11-03T10:30:00Z"}              │
│  │   ├─> Update manifest with message count                 │
│  │   └─> Return message_id                                  │
│  ├─> AISDKOrchestrator.send_message(session_id, content)    │
│  │   ├─> Load prompt blocks from registry                   │
│  │   │   (e.g., "system_prompt_dashboard_creation")         │
│  │   ├─> Load last 20 messages from GCS JSONL               │
│  │   ├─> Build prompt with cache-control headers:           │
│  │   │   [{role: "system", content: "...",                  │
│  │   │     cache_control: {type: "ephemeral"}},             │
│  │   │    {role: "user", content: "Show me..."}]            │
│  │   ├─> Call provider API (Claude/OpenAI/Google)           │
│  │   ├─> Stream response as SSE events:                     │
│  │   │   event: token, data: {"content": "I'll"}            │
│  │   │   event: token, data: {"content": " create"}         │
│  │   │   event: tool_call, data: {"tool": "bigquery_query"} │
│  │   ├─> Log model call:                                    │
│  │   │   model_calls(session_id, provider, model,           │
│  │   │                input_tokens, output_tokens,          │
│  │   │                cached_input_tokens, cost_usd,        │
│  │   │                latency_ms)                            │
│  │   ├─> Handle tool calls (if any)                         │
│  │   ├─> Append assistant response to GCS JSONL             │
│  │   ├─> Update manifest: total_tokens, total_cost_usd      │
│  │   └─> Send final SSE event: complete                     │
│  └─> Response: SSE stream until complete                    │
└─────────────────────────────────────────────────────────────┘
```

**Flow: Execute Tool**

```
┌─────────────┐
│   LLM       │
│   Agent     │
└──────┬──────┘
       │ 3. Tool call requested: bigquery_query
       ▼
┌─────────────────────────────────────────────────────────────┐
│  POST /api/v1/sessions/{session_id}/tools                   │
│  ├─> AISDKOrchestrator.execute_tool(tool_name, args)        │
│  │   ├─> Generate cache key:                                │
│  │   │   tool:bigquery_query:{sha256(args)}                 │
│  │   ├─> Check tool_cache table:                            │
│  │   │   SELECT * FROM tool_cache                           │
│  │   │   WHERE cache_key = '...'                            │
│  │   │   AND expires_at > NOW()                             │
│  │   ├─> Cache HIT:                                         │
│  │   │   ├─> Read payload from GCS                          │
│  │   │   ├─> Increment hit_count                            │
│  │   │   ├─> Log cache hit in traces                        │
│  │   │   └─> Return cached result                           │
│  │   ├─> Cache MISS:                                        │
│  │   │   ├─> Execute tool logic (e.g., run BigQuery query)  │
│  │   │   ├─> Validate result against schema                 │
│  │   │   ├─> Upload result to GCS                           │
│  │   │   ├─> Insert into tool_cache table                   │
│  │   │   └─> Return fresh result                            │
│  │   ├─> Log tool execution in tool_calls table             │
│  │   └─> Return {tool_call_id, result, cached}              │
│  ├─> SessionService.add_tool_result(session_id, result)     │
│  │   ├─> Append tool result message to GCS JSONL            │
│  │   └─> Update manifest                                    │
│  └─> Response: {tool_call_id, result, cached, latency_ms}   │
└─────────────────────────────────────────────────────────────┘
```

**Flow: Get Session History**

```
┌─────────────┐
│   User      │
│ (Chat UI)   │
└──────┬──────┘
       │ 4. Load previous conversation
       ▼
┌─────────────────────────────────────────────────────────────┐
│  GET /api/v1/sessions/{session_id}                          │
│  ├─> SessionService.get_session(session_id)                 │
│  │   ├─> Load Postgres pointer:                             │
│  │   │   SELECT * FROM sessions WHERE id = session_id       │
│  │   ├─> Load manifest from GCS:                            │
│  │   │   gs://bridge-sessions/{session_id}/manifest.json    │
│  │   ├─> Read last 100 messages from JSONL chunks:          │
│  │   │   gs://.../messages-0001.jsonl (parse, reverse)      │
│  │   │   gs://.../messages-0002.jsonl (if exists)           │
│  │   ├─> Query model_calls for session:                     │
│  │   │   SELECT SUM(input_tokens), SUM(output_tokens),      │
│  │   │          SUM(cost_usd)                                │
│  │   │   FROM model_calls WHERE session_id = ...            │
│  │   ├─> Enrich response with metrics:                      │
│  │   │   {session, messages, total_tokens, total_cost}      │
│  │   └─> Return enriched session                            │
│  └─> Response: {session_id, messages, metrics, artifacts}   │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Decisions**

1. **Manifest is Append-Only**: Messages are added via JSONL append, never modified. Immutable audit trail.
2. **Postgres Stores Pointers Only**: `sessions` table contains `session_id` + `gcs_path`, not full message content. Keeps DB lean.
3. **GCS is Source of Truth**: All message content lives in GCS JSONL files. Postgres is metadata index only.
4. **JSONL Chunking**: Messages rotate to new chunk after 10K tokens or 1000 messages. Prevents single file bloat.
5. **Model Calls Always Logged**: Every LLM API call tracked in `model_calls` table with tokens and cost. Enables budget enforcement.
6. **Tool Cache is Deterministic**: Same tool + same args → same cache key → instant cache hit. Reduces costs and latency.

**Message Storage Format (JSONL)**

```jsonl
{"id": "msg_001", "role": "user", "content": "Show revenue for Q4", "timestamp": "2025-11-03T10:30:00Z"}
{"id": "msg_002", "role": "assistant", "content": "I'll query BigQuery for Q4 revenue data.", "timestamp": "2025-11-03T10:30:05Z"}
{"id": "msg_003", "role": "tool", "tool_call_id": "call_001", "tool_name": "bigquery_query", "result": {...}, "timestamp": "2025-11-03T10:30:10Z"}
{"id": "msg_004", "role": "assistant", "content": "Here's your Q4 revenue dashboard...", "timestamp": "2025-11-03T10:30:15Z"}
```

### **5. Caching & Freshness Model**

### **5.1 BigQuery Result Cache**

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

### **5.2 Tool Execution Cache (Deterministic Caching)**

The tool cache eliminates redundant expensive operations (BigQuery queries, API calls, file operations) through deterministic key generation.

**Cache Key Generation**

```python
import hashlib
import json

def generate_tool_cache_key(tool_name: str, args: dict) -> str:
    # Canonicalize args: sort keys, remove null values, consistent formatting
    canonical_args = json.dumps(args, sort_keys=True, ensure_ascii=True)
    args_hash = hashlib.sha256(canonical_args.encode()).hexdigest()
    return f"tool:{tool_name}:{args_hash}"

# Example
args = {"table": "mart.revenue_daily", "date_range": "last_90_days"}
key = generate_tool_cache_key("bigquery_query", args)
# Result: "tool:bigquery_query:a3f5e9..."
```

**Storage Pattern**

- **Metadata in Postgres**: `tool_cache` table stores key, tool_name, TTL, expires_at, hit_count
- **Payload in GCS**: `gs://bridge-cache/{tenant_id}/{tool_name}/{args_hash}.json`
- **Why split storage?** Postgres enables fast TTL expiry queries; GCS handles large payloads efficiently

**TTL Strategy by Tool Type**

| Tool Type | TTL | Rationale |
|-----------|-----|-----------|
| Short-lived (e.g., current_time, random_value) | 1 minute | Values change frequently |
| Stable (e.g., schema_query, metadata_lookup) | 24 hours | Schemas rarely change |
| Expensive (e.g., large BigQuery scans, external APIs) | 7 days | High cost justifies longer cache |
| User-specific (e.g., user_preferences) | 1 hour | Balance freshness and performance |

**Cache Hit/Miss Flow**

```python
async def execute_tool_with_cache(tool_name: str, args: dict):
    # Generate deterministic cache key
    cache_key = generate_tool_cache_key(tool_name, args)

    # Check cache (Postgres + GCS)
    cache_entry = await db.query(ToolCache).filter_by(
        cache_key=cache_key
    ).filter(
        ToolCache.expires_at > datetime.utcnow()
    ).first()

    if cache_entry:
        # Cache HIT
        payload = await gcs.download_json(cache_entry.gcs_payload_uri)
        await db.execute(
            update(ToolCache).where(ToolCache.id == cache_entry.id).values(
                hit_count=ToolCache.hit_count + 1,
                last_accessed=datetime.utcnow()
            )
        )
        return {"result": payload, "cached": True}

    # Cache MISS - execute tool
    result = await execute_tool_logic(tool_name, args)

    # Store in cache
    gcs_uri = await gcs.upload_json(
        f"gs://bridge-cache/{tool_name}/{args_hash}.json",
        result
    )

    ttl = get_ttl_for_tool(tool_name)  # From config
    await db.add(ToolCache(
        tool_name=tool_name,
        cache_key=cache_key,
        gcs_payload_uri=gcs_uri,
        ttl_seconds=ttl,
        expires_at=datetime.utcnow() + timedelta(seconds=ttl)
    ))

    return {"result": result, "cached": False}
```

**Cache Invalidation**

1. **Time-based**: Automatic expiry when `expires_at < NOW()`
2. **Manual**: Admin endpoint `DELETE /v1/cache/tools/{tool_name}` clears all cache for a tool
3. **Version-based**: Tool definition change (code update) increments version, invalidates old cache
4. **Selective**: `DELETE /v1/cache/tools/{tool_name}/{args_hash}` clears specific cache entry

**Benefits**

- **Cost Reduction**: Avoid re-running expensive BigQuery queries (save $$$ on bytes scanned)
- **Latency Reduction**: Cache hits return in <50ms vs seconds for BigQuery execution
- **Determinism**: Same inputs always yield same cache key → predictable behavior
- **Observability**: `hit_count` field tracks cache effectiveness per tool

### **5.3 Prompt Block Caching (Anthropic Cache-Control)**

Anthropic's prompt caching reduces costs by 90% on repeated context. We leverage this through a prompt block registry.

**Cache-Control Types**

- **Ephemeral**: 5-minute cache lifetime, suitable for conversation context
- **Static**: Not supported in current Anthropic API, but blocks can be reused across sessions

**Prompt Block Registry Pattern**

```python
# Stored in prompt_blocks table
PROMPT_BLOCKS = {
    "system_prompt_dashboard_creation": {
        "block_type": "system",
        "content": """You are Peter, an AI assistant specialized in creating data dashboards.
Your goal is to help users transform natural language requests into YAML dashboard definitions.
You have access to BigQuery datasets and can query schema information.
Always validate SQL queries before including them in dashboards.""",
        "cache_control": {"type": "ephemeral"},  # Cache for 5 minutes
        "version": 1
    },
    "bigquery_schema_context": {
        "block_type": "system",
        "content": """Available BigQuery datasets and tables:
- mart.revenue_daily (date, region, product_id, revenue, quantity)
- mart.user_activity (date, user_id, event_type, session_id)
- mart.product_catalog (product_id, product_name, category, price)
...""",
        "cache_control": {"type": "ephemeral"},  # Cache for 5 minutes
        "version": 1
    },
    "context_budget_policy": {
        "block_type": "system",
        "content": """Context Budget Policy:
- Maximum 8000 tokens per request
- Summarize conversations after 50 messages
- Drop old messages to stay within budget""",
        "cache_control": {"type": "ephemeral"},
        "version": 1
    }
}
```

**Usage in API Calls**

```python
async def send_message_with_caching(session_id: str, user_message: str):
    # Load prompt blocks
    system_prompt = await prompt_block_service.get_block("system_prompt_dashboard_creation")
    schema_context = await prompt_block_service.get_block("bigquery_schema_context")

    # Build messages with cache-control
    messages = [
        {
            "role": "system",
            "content": system_prompt.content,
            "cache_control": {"type": "ephemeral"}  # Anthropic will cache this
        },
        {
            "role": "system",
            "content": schema_context.content,
            "cache_control": {"type": "ephemeral"}  # And this
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    # Call Claude API
    response = await claude_client.messages.create(
        model="claude-sonnet-4-5",
        messages=messages
    )

    # Log cache usage
    await model_calls_service.log(
        session_id=session_id,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        cached_input_tokens=response.usage.cache_read_input_tokens,  # From Anthropic response
        cost_usd=calculate_cost(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cached_input_tokens=response.usage.cache_read_input_tokens
        )
    )
```

**Cost Savings Example**

Without caching:
- System prompt: 500 tokens × $0.003/1K = $0.0015 per call
- Schema context: 1000 tokens × $0.003/1K = $0.003 per call
- 100 calls/day: $0.45/day = $13.50/month

With caching (90% cache hit rate):
- First call: $0.0015 + $0.003 = $0.0045
- Subsequent 9 calls (cached): (500 + 1000) × $0.0003/1K × 9 = $0.00405
- 10 calls total: $0.00855 → $0.86/day = $25.80/month (vs $135 without caching)
- **Savings: 81% reduction**

**Cache Efficiency Metrics**

```sql
-- Calculate cache hit rate from model_calls table
SELECT
    COUNT(*) AS total_calls,
    SUM(cached_input_tokens) AS total_cached_tokens,
    SUM(input_tokens) AS total_input_tokens,
    ROUND(100.0 * SUM(cached_input_tokens) / NULLIF(SUM(input_tokens), 0), 2) AS cache_hit_rate_pct,
    SUM(cost_usd) AS total_cost_usd,
    -- Estimated cost without caching (all tokens at full price)
    SUM(input_tokens) * 0.003 / 1000 + SUM(output_tokens) * 0.015 / 1000 AS cost_without_cache_usd,
    ROUND(100.0 * (1 - SUM(cost_usd) / NULLIF(SUM(input_tokens) * 0.003 / 1000 + SUM(output_tokens) * 0.015 / 1000, 0)), 2) AS savings_pct
FROM model_calls
WHERE created_at >= NOW() - INTERVAL '7 days';
```

**Best Practices**

1. **Cache Long Static Content**: System prompts, schema definitions, documentation
2. **Don't Cache User Input**: Only cache reusable blocks, not conversation-specific content
3. **Version Prompt Blocks**: Increment version on content change to avoid stale cache
4. **Monitor Cache Efficiency**: Track `cached_input_tokens` ratio in observability dashboards
5. **Budget for Cache Misses**: First call to new session incurs full cost; budget accordingly

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

### **7.1 Model Call Logging & Cost Tracking**

Every LLM API call is logged in the `model_calls` table for cost tracking, budget enforcement, and cache efficiency analysis.

**Logged Metrics Per Call**

```python
# After every LLM API call
await model_calls_service.log(
    session_id=session_id,
    provider="anthropic",  # anthropic | openai | google
    model="claude-sonnet-4-5",
    input_tokens=response.usage.input_tokens,
    output_tokens=response.usage.output_tokens,
    cached_input_tokens=response.usage.cache_read_input_tokens,  # Anthropic only
    latency_ms=int((time.time() - start_time) * 1000),
    cache_hit=response.usage.cache_read_input_tokens > 0,
    cost_usd=calculate_cost(...),  # From pricing table
    purpose="chat"  # chat | verification | summarization
)
```

**Pricing Table (Example)**

```python
PRICING = {
    "anthropic": {
        "claude-sonnet-4-5": {
            "input": 0.003 / 1000,  # $0.003 per 1K tokens
            "output": 0.015 / 1000,  # $0.015 per 1K tokens
            "cached_input": 0.0003 / 1000  # 90% discount on cached tokens
        },
        "claude-opus-4": {
            "input": 0.015 / 1000,
            "output": 0.075 / 1000,
            "cached_input": 0.0015 / 1000
        }
    },
    "openai": {
        "gpt-4-turbo": {
            "input": 0.01 / 1000,
            "output": 0.03 / 1000
        }
    }
}

def calculate_cost(provider: str, model: str,
                   input_tokens: int, output_tokens: int,
                   cached_input_tokens: int = 0) -> float:
    pricing = PRICING[provider][model]
    cost = (
        (input_tokens - cached_input_tokens) * pricing["input"] +
        cached_input_tokens * pricing.get("cached_input", pricing["input"]) +
        output_tokens * pricing["output"]
    )
    return round(cost, 6)
```

**Aggregation Queries**

```sql
-- Total cost per session
SELECT
    session_id,
    COUNT(*) AS total_calls,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens,
    SUM(cached_input_tokens) AS total_cached_tokens,
    SUM(cost_usd) AS total_cost_usd,
    AVG(latency_ms) AS avg_latency_ms
FROM model_calls
GROUP BY session_id;

-- Cost breakdown by model (last 7 days)
SELECT
    provider,
    model,
    COUNT(*) AS calls,
    SUM(input_tokens + output_tokens) AS total_tokens,
    SUM(cost_usd) AS total_cost_usd,
    ROUND(AVG(latency_ms), 2) AS avg_latency_ms
FROM model_calls
WHERE executed_at >= NOW() - INTERVAL '7 days'
GROUP BY provider, model
ORDER BY total_cost_usd DESC;

-- Cache efficiency
SELECT
    DATE(executed_at) AS date,
    COUNT(*) AS total_calls,
    SUM(cached_input_tokens) AS cached_tokens,
    SUM(input_tokens) AS total_input_tokens,
    ROUND(100.0 * SUM(cached_input_tokens) / NULLIF(SUM(input_tokens), 0), 2) AS cache_hit_rate_pct,
    SUM(cost_usd) AS daily_cost_usd
FROM model_calls
WHERE executed_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(executed_at)
ORDER BY date DESC;

-- Budget alerts (monthly spend by user)
SELECT
    s.user_id,
    u.email,
    COUNT(DISTINCT s.id) AS session_count,
    SUM(mc.cost_usd) AS monthly_cost_usd,
    CASE
        WHEN SUM(mc.cost_usd) > 100 THEN 'CRITICAL'
        WHEN SUM(mc.cost_usd) > 50 THEN 'WARNING'
        ELSE 'OK'
    END AS budget_status
FROM model_calls mc
JOIN sessions s ON mc.session_id = s.id
JOIN users u ON s.user_id = u.id
WHERE mc.executed_at >= DATE_TRUNC('month', NOW())
GROUP BY s.user_id, u.email
HAVING SUM(mc.cost_usd) > 10  -- Only show users with >$10 spend
ORDER BY monthly_cost_usd DESC;
```

**Budget Enforcement**

```python
async def enforce_budget(session_id: str) -> bool:
    # Check monthly budget
    monthly_cost = await db.query(
        func.sum(ModelCall.cost_usd)
    ).join(
        Session
    ).filter(
        Session.user_id == current_user.id,
        ModelCall.executed_at >= func.date_trunc('month', func.now())
    ).scalar()

    if monthly_cost >= settings.monthly_llm_budget_usd:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly LLM budget exceeded: ${monthly_cost:.2f} / ${settings.monthly_llm_budget_usd}"
        )

    return True
```

**OpenTelemetry Spans for Model Calls**

```python
with tracer.start_as_current_span("llm.model_call") as span:
    span.set_attribute("session.id", session_id)
    span.set_attribute("model.provider", provider)
    span.set_attribute("model.name", model)
    span.set_attribute("model.input_tokens", input_tokens)
    span.set_attribute("model.output_tokens", output_tokens)
    span.set_attribute("model.cached_input_tokens", cached_input_tokens)
    span.set_attribute("model.cost_usd", cost_usd)
    span.set_attribute("model.latency_ms", latency_ms)
    span.set_attribute("model.cache_hit", cache_hit)
    span.set_attribute("model.purpose", purpose)
```

**Metrics Dashboard (Grafana/Cloud Monitoring)**

Key metrics to track:
- Total cost over time (daily/weekly/monthly trends)
- Cost by provider and model
- Token usage by purpose (chat vs verification vs summarization)
- Cache hit rate (cached_input_tokens / total_input_tokens)
- Average latency by model
- Error rate by provider
- Budget utilization (current spend vs monthly limit)

**Cost Alert Thresholds**

```python
# settings.py
COST_ALERT_THRESHOLDS = {
    "daily": {
        "warning": 50,   # $50/day
        "critical": 100  # $100/day
    },
    "monthly": {
        "warning": 800,  # 80% of $1000 budget
        "critical": 950  # 95% of budget
    }
}
```

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
| Universal AI SDK Integration (Phase 2.12) | ⏳ Planned | docs/task.md (Phase 2.12) | GCS-backed session storage, model call logging, tool caching, prompt block registry—enables LLM-driven dashboard creation with cost tracking and deterministic caching. |

**Outstanding follow-ups**
- Replace placeholder responses in DataServing/Precompute with real execution + cache writes before declaring PDR §5 complete.
- Implement guardrail backlog (SQL sanitiser, dataset allowlist, cache TTL/purge) to satisfy Risk 2 & Risk 3 mitigations.
- Wire bytes_scanned + latency metrics into every response/log per docs/task.md Phase 4.

### **12.2 Decision Log (Updated)**
- **YAML SSOT migration (2025-10-31)** — Dashboard definitions now stored exclusively in `/dashboards/*.yaml`; Postgres `dashboards` table deprecated. Rationale: eliminate drift, simplify deploy surface, improve developer ergonomics (git reviewable configs). Value: reduces 200–300 LoC, removes periodic sync job.
- **Schema Browser cost posture** — Adopted BigQuery `datasets.list` + `tabledata.list` APIs only (no billed query jobs). Ensures zero-cost browsing while meeting PDR §9 cost guardrails.
- **Async compliance sweep** — Converted blocking service methods to async/await (see docs/task.md Phase 2 deliverables). Keeps event loop free for chat + precompute workloads.
- **ADR-001: Postgres as Directory, GCS as Data Lake (2025-11-03)** — Session messages stored in GCS JSONL files, not Postgres. Rationale: Postgres optimized for metadata queries, not large blobs; GCS cheaper and scales to 1000+ message conversations. Postgres stores only pointers (`session_id`, `gcs_path`). Value: DB stays <1 GB even with 10K active sessions; query performance remains sub-100ms.
- **ADR-002: Universal AI SDK Layer (2025-11-03)** — Abstract orchestrator interface wraps provider-specific SDKs (Claude, OpenAI, Google). Rationale: Single codebase for multi-provider support; easy to switch providers or A/B test models. Trade-off: Initial complexity for long-term flexibility. Value: Reduces vendor lock-in, enables cost optimization via provider arbitrage.
- **ADR-003: Deterministic Tool Caching (2025-11-03)** — Tool results cached with SHA-256 hash of canonicalized args as key. Rationale: Same inputs → same cache key → instant cache hit; reduces BigQuery costs and latency. Implementation: Split storage (Postgres metadata + GCS payload) for fast TTL queries + large result handling. Value: 80%+ cache hit rate on stable tools saves ~$500/month on BigQuery.
- **ADR-004: Model Call Logging for Cost Tracking (2025-11-03)** — Every LLM API call logged in `model_calls` table with token counts and cost. Rationale: Budget enforcement, cost attribution, cache efficiency analysis. Overhead: +50ms per call for DB INSERT, negligible vs LLM latency. Value: Enables per-user cost caps, prevents runaway spend, tracks cache ROI.
- **ADR-005: Anthropic Prompt Caching Integration (2025-11-03)** — Use Anthropic cache-control headers for static prompt blocks. Rationale: 90% cost reduction on cached tokens (~5-minute cache lifetime). Implementation: Prompt block registry in DB, cache-control injected automatically. Constraint: Only works with Anthropic; other providers need fallback. Value: Reduces monthly LLM spend by 60-80% in typical usage patterns.

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
