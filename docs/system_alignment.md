# 🧭 System Realignment & Decision Summary — Agentic System Stack

**Version:** 1.0  
**Date:** Nov 2025  
**Author:** System Architecture Working Notes  

---

## ⚡ Summary — Next Steps & Key Action Points

| Area | Decision | Action Owner | Priority |
| :-- | :-- | :--: | :--: |
| **Architecture Split** | Keep **FastAPI backend** as *Universal AI SDK* host (Claude Agent SDK, tool orchestration, caching, context), and **Vercel AI SDK frontend** purely for chat/streaming UX. | Backend / Frontend leads | ✅ High |
| **Storage Strategy** | Store **long-form content (messages, tool outputs, artifacts)** in **GCS**, and keep **only metadata & summaries** in **Postgres**. Avoid duplication. | Infra | ✅ High |
| **Sessions & Context** | Each session = single source of truth for change logs. Dashboards/Teams derive context from sessions. No separate “update logs.” | Backend | ✅ High |
| **Artifacts & Caches** | Retain Postgres “index” for GCS artifacts & deterministic tool caches. Payloads live in GCS only. | Backend | ✅ High |
| **Prompt & Model Calls** | Keep prompt-block table for Anthropic caching; log all model calls + token/cost metadata. | Backend | Medium |
| **Frontend Chat** | Vercel AI SDK + AI UI for chat/streaming; backend streaming over SSE/WS. | Frontend | ✅ High |
| **YAML Source of Truth** | Dashboards remain YAML-in-Git (linked to commit SHA in Postgres). | Full-stack | ✅ High |
| **Context Policy** | Maintain rolling summaries in Postgres; full history in GCS; enforce per-session context budget. | Backend | Medium |
| **Migration Scope** | Modify existing backend & frontend PDR implementations to adopt new storage layout + SDK responsibilities. | Arch | ✅ High |

---

## 🧩 Current vs Target — Overview

| Layer | Current State (from PDRs) | Required Change |
| :-- | :-- | :-- |
| **Backend (FastAPI)** | Monolithic API running on GCP Cloud Run; handles YAML validation, SQL execution, storage via FS; no true AI orchestration. | Refactor into **Universal AI SDK host**. Integrate Claude Agent SDK, tool cache, prompt registry, GCS I/O. Create session manifest table + model_calls log. Remove raw message persistence in DB. |
| **Frontend (Next.js + ShadCN)** | Uses planned `useChat` hook & SSE for chat; structured 3-panel dashboard; no SDK yet. | Replace custom SSE logic with **Vercel AI SDK** for chat streaming + dynamic tool forms. Simplify state logic to rely on backend session IDs. |
| **Storage / Data Stack** | Mix of local FS + GCS placeholder. Artifacts unstructured. | Adopt **GCS-first pattern**. Store long content, messages, artifacts, and cache payloads under structured paths. Use Postgres only for metadata, pointers, and cost logs. |
| **UI / UX** | Wireframes show Assistant pane but no clarity on persistent state or context resume. | Update UX flow: add *Session continuity* (resume, summarize, archive). Show cost/tokens from backend logs. Add “Open YAML” and “Link to Git Commit” buttons in dashboard views. |
| **Auth & Tenancy** | Google SSO with Postgres users; no tenant enforcement. | Extend models with `tenant_id`; add per-tenant GCS prefixes & RLS policies. |
| **Caching / Performance** | Result caching exists for BigQuery only. | Add `tool_cache` for deterministic tool outputs. Use Anthropic prompt caching for static blocks. |
| **Observability / Cost** | Logs BigQuery costs only. | Add `model_calls` log for LLM tokens, cost, latency, cache hit, and errors. Export via OTel. |

---

## 🧱 Backend Realignment Plan (FastAPI → Universal AI SDK)

### ✅ Keep
- Service-based structure (`YAMLValidationService`, `SQLExecutorService`, etc.)  
- BigQuery pipeline + cost guardrails  
- Auth/session management  
- StorageService (to be extended for GCS)  

### ➕ Add
| Component | Purpose |
| :-- | :-- |
| **Universal AI SDK Layer (Python)** | Core orchestrator. Wraps Anthropic/OpenAI/Google Agent SDKs (starting with Claude). Handles unified API interface, streaming, caching, and model routing. |
| **Claude Agent SDK integration** | Agentic orchestration for multi-step reasoning (file, HTTP, bash, MCP tools). |
| **Session Manifest Table (Postgres)** | Metadata only: `session_id`, `tenant_id`, `team_id`, `dashboard_id`, `gcs_uri`, `summary`, `created_at`. |
| **GCS-backed Message Store** | Append JSONL chunks of full conversation logs; TTL & lifecycle managed in bucket. |
| **Artifacts Table (Index)** | Directory of raw/clean/derived content. Deduplicate by SHA. |
| **Tool Cache Table (Index)** | Key → version → GCS URI → TTL mapping; payload in GCS. |
| **Model Calls Table** | Log provider, model, latency, cost, cached_input flag. |
| **Prompt Blocks Table** | Static reusable prompts for Anthropic cache-control. |

### ⚙️ Modify
- Replace local FS references with GCS signed URLs.  
- Session CRUD → generate bucket paths + maintain minimal DB rows.  
- Logging middleware → record model_calls and tool_cache hits.

### 🧹 Remove
- Full “messages” persistence in DB.  
- Redundant update logs for team/dashboard context.

---

## 🎨 Frontend Realignment Plan (Next.js + Vercel AI SDK)

### ✅ Keep
- Three-panel layout (Explorer / Workspace / Assistant).  
- ShadCN + Tailwind component library.  
- Server Components for auth/session validation.  

### ➕ Add
| Feature | Implementation |
| :-- | :-- |
| **Vercel AI SDK Integration** | Replace manual `useChat` hook with SDK’s `useChat`, `AI UI` components for conversation + streaming. |
| **Tool Form Rendering** | Auto-generate from backend JSON Schemas (from FastAPI tools). |
| **Session Resume** | Fetch session manifest (with summary + GCS log pointer) from backend. |
| **Cost Display** | Display token and cost metrics from backend `model_calls`. |
| **Commit Linking** | “View YAML on GitHub” button using stored commit SHA. |
| **Streaming UX** | Rely on SDK token streaming; show progress, tool calls, status tags. |

### ⚙️ Modify
- Replace raw `/chat/message` SSE handler with `POST /chat` → SSE/WS from backend Universal AI SDK.  
- Refactor Zustand store → session context only (no long-term message caching).

### 🧹 Remove
- Local conversation persistence in FE; rely entirely on backend manifest + GCS.

---

## 🧭 UI/UX Adjustments

| Element | New Design Decision |
| :-- | :-- |
| **Assistant Panel** | Persistent thread list (sessions). Each can be resumed (pulls summary + last turns). |
| **Dashboard YAML View** | Read-only view linked to GitHub commit. “Regenerate via Agent” CTA triggers backend Claude SDK. |
| **Tool Execution Logs** | Lightweight, collapsible sidebar listing tool calls, status, and cache hits (from backend). |
| **Session Summary Cards** | Replace long chat scrolls with summary + last interaction preview (stored in Postgres). |
| **Error & Cost Feedback** | Toasts showing token usage, cache reuse, or rate-limited status from backend metadata. |

---

## ☁️ Storage and Caching Layout

| Type | Store | Lifecycle | Access |
| :-- | :-- | :-- | :-- |
| **Session Logs** | `gs://bucket/sessions/{session_id}/messages-0001.jsonl` | Rotate after 10K tokens; 90-day expiry | Signed URL read |
| **Artifacts** | `gs://bucket/artifacts/{tenant_id}/raw|clean/{sha}` | Versioned | Signed URL read |
| **Tool Cache Payloads** | `gs://bucket/cache/{tenant_id}/{tool}/{key}.json` | 7–30 days | Backend only |
| **Prompt Blocks** | Postgres small table or file bundle | Long-term | Backend only |
| **YAML Dashboards** | GitHub repo (canonical source) | Versioned via commits | Linked in DB |

---

## 🔧 Implementation Adjustments — PDR Deltas

| Document | Current State | Changes Needed |
| :-- | :-- | :-- |
| **backend_pdr.md** | Treats AI logic as future integration; stores all state locally. | Integrate Universal AI SDK + Claude Agent SDK; shift storage to GCS; add metadata tables. Remove full `messages` persistence. |
| **frontend_pdr.md** | Defines SSE-based chat + manual stream parsing. | Replace with Vercel AI SDK hooks + dynamic tool form rendering. Remove manual SSE code. |
| **ui_pdr.md / ux_wireframes.md** | UI shows chat, but no persistence or cost summary. | Add “Session Resume” + “Token Summary” elements. Replace local logs with backend streaming endpoint. |
| **task.md** | Lists parallel efforts for data stack, admin, and chat. | Merge “chat” and “AI orchestration” tasks under Universal SDK integration. Defer vector DB until triggers met. |
| **cli_reference.md** | Focused on CLI orchestration, not cloud cache. | Add commands for inspecting session manifests, cache stats, and GCS URIs. |

---

## 📊 Future Expansion Hooks

| Trigger | Next Component |
| :-- | :-- |
| >5k artifacts or fuzzy search needs | Add pgvector + semantic_search tool |
| Multi-tenant scaling | Enable RLS + per-tenant quotas in model_calls |
| High replay cost | Extend GCS cache to memoize entire model responses (Anthropic cache + local TTL) |
| Analytics | Add dashboard summarizer (periodic) using context_snapshots |

---

## ✅ Final Architecture Snapshot

```
Frontend (Vercel / Next.js)
│
│ useChat() + AI UI  →  FastAPI /chat (SSE/WS)
│
└── Backend (FastAPI - Universal AI SDK)
     ├── Claude Agent SDK (tools, reasoning)
     ├── Google Agent SDK (planned)
     ├── OpenAI Agent SDK (planned)
     ├── GCS Storage Adapter
     ├── Postgres (metadata only)
     │     ├── sessions_manifest
     │     ├── model_calls
     │     ├── artifacts
     │     ├── tool_cache
     │     └── prompt_blocks
     └── GitHub YAML source (dashboards)
```

---

## 📌 Takeaway Principles

1. **Single source of truth per domain:**  
   - YAML (Dashboards) → GitHub  
   - Sessions → GCS logs + Postgres manifest  
   - Caches → GCS payload + Postgres index  

2. **Postgres = Directory, not Warehouse**  
   Metadata, summaries, and pointers — never bulk logs.

3. **GCS = Long-form memory**  
   Cheap, versioned, lifecycle-managed storage for chat, tools, and artifacts.

4. **Frontend = Presentation layer**  
   No AI logic, no provider keys, only UX + streaming.

5. **Universal AI SDK (Backend)**  
   Orchestrates all model calls, prompt caching, context summarization, and logging.

