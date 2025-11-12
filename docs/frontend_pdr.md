
## **PDR — Frontend (MVP)**

### **1. Problem & Goals (MVP)**

**Problem**  
Users need intuitive visual dashboards but lack SQL expertise. Current processes involve manual chart creation, brittle data pipelines, and no version control. Analysts spend hours building one-off visualizations instead of reusable dashboards. No visibility into data freshness or query lineage.

**Goals**  
- Render interactive, production-quality dashboards from YAML definitions without requiring users to understand underlying structure
- Enable natural language dashboard creation through LLM chat interface with verified SQL results
- Provide two-way editing: UI changes reflect back into YAML; YAML changes render immediately in UI
- Display data freshness explicitly per visualization so users understand recency
- Deliver clean, minimal, accessible interface using modern component library
- Support explicit save workflow with dirty state tracking to prevent accidental loss

### **2. Scope & Non-Goals (MVP)**

**In Scope**  
- Application shell with three-panel layout: explorer, workspace, assistant
- YAML-to-UI rendering engine mapping dashboard definitions to visual components
- Chart library integration for standard visualization types: line, bar, area, pie, table
- LLM chat panel for dashboard creation and modification via natural language
- YAML editor with syntax highlighting and validation feedback
- Save workflow with dirty state indicator and confirmation dialogs
- Lineage visualization showing dashboard composition and data sources
- Authentication integration with Google SSO
- Freshness indicators showing as-of timestamp per chart
- Basic responsive layout for desktop viewing

**Out of Scope**  
- Real-time collaborative editing with operational transforms
- Offline-first architecture with local storage and sync
- Mobile-optimized views or native mobile apps
- Advanced chart customization beyond color and basic formatting
- Custom JavaScript-based chart types
- Dashboard templating or cloning workflows
- Export to PDF or PowerPoint
- Scheduled email reports
- Dashboard versioning UI beyond basic save history

### **3. Architecture Overview**

**Framework and Routing**
Next.js App Router provides foundation. Server components handle authentication and initial data fetching. Client components manage interactive state. File-based routing: dashboard view, edit mode, new dashboard wizard, settings. Middleware validates session on protected routes.

**Component Architecture**
Top-level App Shell wraps all views. Explorer sidebar lists available dashboards and datasets. Workspace tabs hold active dashboard views and editors. Assistant panel contains LLM chat interface with collapsible sections. All components built with ShadCN/UI primitives for consistency.

**AI Integration Layer**
Frontend acts as pure display layer for backend's Universal AI SDK. Vercel AI SDK (`ai` package) handles streaming UX via `useChat()` hook consuming backend `/chat` SSE endpoint. Backend orchestrates all LLM calls (Claude, OpenAI, Gemini, Bedrock), provider selection, tool execution, and cost tracking. Frontend receives streamed responses and displays progressively. No direct provider integrations in frontend—all AI logic remains server-side. Tool execution status (pending, executing, completed) streamed from backend and rendered in UI. Cost and token metadata calculated by backend, displayed in real-time via session API.

**State Management**
Zustand stores organized by domain: **Session Store** (current session metadata: ID, user, provider, total cost, total tokens), **Chat Store** (optimistic message updates, pending tool approvals), **Dashboard Store** (active YAML model, dirty flag, last save timestamp). Session store hydrates once on app mount from `/sessions/current` endpoint. Chat messages cached via TanStack Query for history viewing. No persistence beyond session for MVP—backend GCS storage is source of truth. Changes held in memory until explicit save triggers backend API call.

**Data Flow**
Server-side rendering fetches dashboard metadata on route load. Client components request chart data from backend API. Responses cached in React Query for efficient re-renders. Chat messages stream via SSE from backend `/chat` endpoint, handled by Vercel AI SDK. UI mutations update in-memory YAML model. Save action posts YAML to backend, receives confirmation, resets dirty flag. Session cost/tokens update automatically as messages complete.

**Styling System**
Tailwind CSS provides utility-first styling. ShadCN components offer pre-built accessible patterns. Design tokens define spacing, colors, typography following minimal aesthetic. Light and dark modes supported via CSS variables. Custom theme variations possible without component changes.

**Chart Rendering**
Recharts library renders all visualizations. Data arrives as arrays from backend. Chart configurations derived from YAML metadata: chart type, axes, colors, legend placement. Responsive containers handle window resizing. Loading skeletons show during fetch. Error boundaries catch rendering failures gracefully.

### **4. Data & Control Flows**

**Dashboard View Load Flow**  
User navigates to dashboard URL with slug identifier. Next.js middleware validates session cookie. Server component fetches dashboard metadata from backend API. Server pre-renders layout structure. Client component hydrates and requests chart data via GET data endpoint. Backend returns compact payloads with as-of timestamps. Client renders charts using Recharts with data props. Freshness badges display timestamps. User interacts with charts: zoom, hover for tooltips, legend toggles.

**LLM-Assisted Dashboard Creation Flow**
User clicks "New Dashboard" button. Frontend shows chat interface with example prompts. User types natural language request describing desired visualization. Frontend sends message via Vercel AI SDK `useChat()` hook to backend `/chat` endpoint with current session ID. Backend Universal AI SDK coordinates LLM (Claude/OpenAI/Gemini) which generates YAML. Backend verifies SQL queries through execution loop. Backend streams response via SSE including YAML, verification results, and sample data. Frontend progressively renders streamed chunks. Frontend parses YAML into in-memory model and displays preview. User reviews and optionally requests modifications through continued chat. Backend updates session cost/tokens after each LLM call. Final edit triggers save action posting to backend.

**Chat Message Streaming Flow**
User types message in assistant panel input. Frontend calls `useChat().append()` with message content and session ID. Backend receives `POST /chat` request, validates session, invokes Universal AI SDK. Backend streams SSE events: `text` chunks (progressive message content), `tool_call` events (tool name, args, status), `cost_update` events (tokens used, cost incurred). Frontend `useChat()` hook processes stream, updates message list in real-time. Tool calls render as inline cards with status (pending → executing → completed). Cost counter updates immediately on `cost_update` events. Errors streamed as `error` events, displayed in error banner. On completion, backend persists full conversation to GCS, frontend caches message in TanStack Query.

**Two-Way Edit Flow**  
User viewing rendered dashboard clicks "Edit" button. UI toggles to edit mode showing properties panel. User changes chart color via color picker. Frontend updates in-memory YAML model at specific path. Renderer re-evaluates model and updates chart instantly. Dirty flag sets to true, UI shows unsaved indicator. User clicks "Save" button. Frontend validates YAML structure locally. Frontend posts to backend save endpoint with YAML payload. Backend writes to storage and returns confirmation. Frontend resets dirty flag, shows success toast, updates last save timestamp.

**YAML Editor Synchronization**  
User toggles to YAML editor tab. Editor displays full YAML text from in-memory model. User edits YAML directly: changes query, adds new chart definition. Editor runs client-side schema validation on keystroke debounce. Syntax errors highlighted inline with messages. On valid YAML, in-memory model updates. If user toggles back to visual view, renderer reflects changes immediately. Save workflow identical to UI-driven edits.

**Lineage Exploration Flow**  
User clicks "View Lineage" button on dashboard. Frontend requests lineage data from backend endpoint. Backend returns graph JSON: nodes (dashboard, charts, queries, tables) and edges (relationships). Frontend renders interactive graph using force-directed layout or hierarchical tree. User clicks node to see metadata panel: query SQL, table schema, row counts. User can click "Explain this" to open chat with context pre-filled about selected node. LLM provides natural language explanation of data flow.

### **5. Caching & Freshness Model**

**Frontend Caching**  
React Query caches all API responses keyed by URL and parameters. Dashboard metadata cached with stale time of 5 minutes. Chart data cached with stale time of 10 minutes. Background refetch triggered on window focus. Manual refresh button bypasses cache and requests fresh data. No persistent storage: cache evicts on page close.

**Freshness Display**  
Every chart card displays timestamp badge: "As of Oct 30, 7:15 AM." Timestamp derived from backend response metadata. Color coding indicates age: green under 1 hour, yellow 1-4 hours, red over 4 hours, gray for unknown. Hover tooltip shows additional context: source table, last refresh trigger. Global dashboard freshness shown in header: "Next refresh: Not scheduled" in MVP.

**Cache Interaction with Backend**  
Frontend never controls backend cache directly. Backend determines cache hits or misses transparently. Frontend receives identical response format regardless. Backend includes cache metadata in response headers for debugging. Frontend can display cache-hit indicator in dev mode only.

**Handling Stale Data**  
When user loads dashboard, frontend shows cached data immediately if available. Background request checks for newer version. If newer data exists, banner appears: "New data available - Click to refresh." User clicks, frontend invalidates cache, fetches fresh data, re-renders charts. Automatic refresh not implemented in MVP to avoid disrupting user exploration.

### **6. Security & Access**

**Authentication Flow**  
Unauthenticated user redirected to Google OAuth login page. After successful authentication, backend sets HTTP-only session cookie. Frontend reads authenticated user context from server component. All API requests include session cookie automatically. Expired sessions return 401, triggering logout and redirect to login.

**Authorization Display**  
Frontend assumes all authenticated users have full access in MVP. Dashboard metadata includes owner email displayed in UI but not enforced. Settings page shows current user email and org affiliation. No role-based UI hiding or permission checks implemented yet.

**CSRF Protection**  
Session cookies marked HTTP-only, Secure, and SameSite=Strict. Next.js CSRF token automatically included in mutation requests. Backend validates token on state-changing operations.

**Content Security**  
No user-supplied HTML rendered; all content from YAML sanitized. Recharts handles data binding safely without innerHTML. External links from dashboard descriptions open in new tab with noopener and noreferrer.

**Secrets Handling**  
No secrets stored in frontend code or environment variables exposed to client. Backend session tokens are opaque identifiers. OAuth tokens never sent to frontend. BigQuery connection strings and service accounts remain server-side only.

### **7. Observability & Lineage**

**Frontend Telemetry**  
Real User Monitoring via Cloud Monitoring or similar. Metrics tracked: page load time, time to interactive, chart render duration, API request latency, error rates. Custom events: dashboard view, edit initiated, save completed, chat message sent. Session recordings not implemented in MVP to avoid privacy concerns.

**Error Handling**  
Global error boundary catches unhandled React errors. Displays friendly message with trace ID for reporting. API errors shown contextually: toast notifications for saves, inline messages for validation failures, dedicated error states for data loading failures. Users can click "Report Issue" to copy trace ID and error details.

**Lineage Visualization**  
Frontend consumes lineage graph JSON from backend. Renders using D3.js or Cytoscape.js for interactive graph. Nodes positioned using automatic layout algorithm. Edges color-coded by relationship type. Pan and zoom enabled. Click interaction shows metadata panel. Lineage view read-only in MVP; future: edit connections, add annotations.

**Performance Monitoring**  
Browser DevTools Lighthouse audits run in CI pipeline. Performance budget enforced: Time to Interactive under 3 seconds, Total Blocking Time under 300ms. Bundle size monitored: main bundle under 200KB gzipped. Failed budgets block deployment to production.

**Logging**
Client-side errors sent to backend logging endpoint with user context and browser info. Logs include: error message, stack trace, user action preceding error, dashboard slug if relevant. PII scrubbed before transmission. Excessive error rates trigger alerts for on-call team.

### **7.1 Chat UI Components & Patterns**

**Assistant Panel Architecture**
Right-side collapsible panel (320px width, resizable). Contains chat interface powered by Vercel AI SDK. Components: ChatContainer (wrapper), MessageList (virtualized with react-window for >100 messages), MessageBubble (role-based styling), InputArea (auto-resize textarea with send button), CostCounter (header display), ProviderIndicator (shows current LLM in use).

**Message Display Patterns**
User messages right-aligned with dark background (`bg-black` light mode, `bg-white` dark mode). Assistant messages left-aligned with light grey (`bg-tertiary`). Timestamps displayed as relative time ("2m ago") in `text-tertiary`. Per-message cost badge shows as small pill next to timestamp (e.g., "$0.0023"). Tool calls render as indented cards within assistant message bubble showing tool name, collapsed args preview, and execution status.

**Tool Execution UI**
ToolCallCard component displays tool invocations inline. States: `pending` (greyed out, no interaction), `executing` (spinner, "Running..." text), `completed` (green checkmark, expandable result panel), `failed` (red X, error message). ToolResultPanel renders below card when expanded, uses syntax highlighting for JSON/code results. All tool orchestration handled by backend—frontend purely displays status updates received via SSE stream.

**Cost & Token Display**
CostCounter fixed in assistant panel header showing cumulative session totals: "$1.23 • 45.2K tokens". Updates in real-time as `cost_update` events arrive via SSE. Color-coded warnings: green (<$1), yellow ($1-5), red (>$5). Per-message badges show individual message cost. No frontend cost calculation—all values from backend session metadata.

**Provider Display**
Read-only indicator in chat header shows current LLM provider selected by backend: "Using Claude 3.5 Sonnet". No provider selection UI in MVP—backend Universal AI SDK chooses provider based on task, cost, availability. Future: admin users can override provider preference via settings.

**Streaming UX**
Progressive text rendering as SSE chunks arrive (word-by-word via Vercel SDK default). Typing indicator ("...") while waiting for first token. Tool call cards appear inline as `tool_call` events stream. Scroll automatically follows latest message unless user has scrolled up manually. "Jump to latest" button appears when user scrolls >100px from bottom.

**Error States**
Network errors show reconnecting toast with countdown. Backend errors display in error banner above input: red background, error message from backend, "Retry" button if retryable. Non-retryable errors show "Copy error details" button including trace ID. Session expired redirects to login immediately.

**Message Caching**
TanStack Query caches messages with key pattern `['session', sessionId, 'messages']`. Stale time set to Infinity (messages immutable once sent). Cache hydrated from `GET /sessions/:id/messages` on panel open. New messages from SSE invalidate cache and trigger re-fetch to ensure consistency with backend GCS storage. Garbage collection after 30 minutes inactive.

### **8. User Journeys**

**Journey 1: First-Time Dashboard Creation via Chat**  
Marketing analyst logs in via Google SSO. Lands on empty dashboard list page. Clicks "New Dashboard" prominent button. Assistant panel expands with welcome message and example prompts. Types: "Show me top 10 products by revenue last quarter with trend comparison to prior quarter." Waits 5-10 seconds while backend processes. Assistant shows progress: "Generating SQL... Verifying results... Building dashboard..." Preview appears in workspace showing table and line chart. Data looks correct. Analyst clicks "Save" button. Prompted for dashboard name and description. Enters "Q3 Product Performance." Save completes. Dashboard appears in explorer sidebar. Analyst clicks to reload and sees persistent dashboard.

**Journey 2: Visual Edit to Change Chart Color**  
Executive opens existing revenue dashboard. Notices bar chart uses blue, wants brand color orange. Clicks "Edit" button. Properties panel appears next to chart. Selects chart by clicking on it, highlights with blue outline. Color picker shows in properties panel with current color. Clicks picker, selects orange from palette. Chart instantly updates to orange bars. Editor shows "Unsaved changes" banner at top. Clicks "Save" button. Confirmation toast appears: "Dashboard saved successfully." Editor no longer shows unsaved banner. Navigates away and returns: color persists as orange.

**Journey 3: Iterative SQL Refinement Through Chat**  
Data engineer creates dashboard with customer churn metrics. Chart shows unexpected spike in September. Suspects SQL logic error. Opens chat panel while viewing dashboard. Types: "The churn metric looks wrong for September. Can you check the calculation?" Assistant responds: "I'll verify the SQL. The query currently uses: [shows SQL snippet]. This counts all cancellations, including trials. Should we exclude trial cancellations?" Engineer confirms: "Yes, exclude trials." Assistant generates revised YAML with updated SQL. Shows before/after sample data in chat. Numbers look correct now. Engineer clicks "Apply Changes" button in chat. Dashboard re-renders with corrected chart. September spike disappears. Engineer saves dashboard with commit message "Fixed churn metric to exclude trial cancellations."

**Journey 4: Exploring Lineage to Understand Data Source**  
Product manager opens user engagement dashboard. Wants to know where active user count comes from. Clicks "View Lineage" icon in header. Graph view opens showing: Dashboard → 3 Charts → 5 Queries → 8 BigQuery Tables. Traces path from "Active Users (Last 30 Days)" chart through query to source table "events.user_activity_daily." Clicks table node. Metadata panel shows: table schema, last updated timestamp, row count, owner team. Clicks "Explain this table" button. Chat opens with context pre-filled. LLM explains: "This table aggregates user events from raw logs, updated daily at 6 AM by the data pipeline. An active user is defined as anyone who performed at least one event in the trailing 30-day window." Manager understands and closes lineage view.

### **9. Performance & Cost Guardrails**

**Render Performance**  
Charts render using Canvas (Recharts default) for better performance with large datasets. Maximum data points per chart set to 500 in backend; more get sampled. Recharts memoization prevents unnecessary re-renders on unrelated state changes. Virtualization considered for long dashboard lists but deferred post-MVP.

**Network Efficiency**  
Single API call per dashboard fetches all chart data in one response. Payload format optimized: timestamps as ISO strings, no redundant metadata per row, chart data pre-aggregated. Compression enabled via Accept-Encoding gzip. Typical dashboard payload under 200 KB compressed.

**Bundle Size**  
Code splitting at route level: dashboard view, edit mode, lineage loaded separately. Heavy dependencies like Recharts only loaded when needed. ShadCN components tree-shaken automatically. Target main bundle under 200 KB gzipped. Monitoring via Bundlephobia or similar.

**Backend Call Optimization**  
React Query deduplicates simultaneous requests for same resource. Prefetching on hover for linked dashboards. Polling avoided; refresh is manual or event-triggered (Phase 1). No unnecessary metadata fetched: only request what UI displays.

**Render Budget**  
Complex dashboards with 10+ charts should render all charts within 2 seconds on modern hardware. Individual chart render under 200ms. Loading skeletons show immediately to maintain perceived performance. Progressive rendering: display charts as data arrives, not all at once.

**Cost Awareness UI**  
Backend returns bytes_scanned in API response. Frontend displays in dev mode or for power users: "This dashboard scanned 2.3 GB to load." Weekly usage email summarizes total bytes per user. No real-time cost displayed in MVP to avoid overwhelming users.

### **10. Risks & Mitigations**

**Risk 1: YAML Complexity Overwhelms Non-Technical Users**  
Users asked to edit YAML directly find syntax errors frustrating. Incorrect indentation or missing quotes break dashboards.  
**Mitigation**: Provide UI-first editing for 90% of common changes. YAML editor available but not primary path. Implement inline validation with helpful error messages. Offer "Repair" button that formats YAML automatically. Include YAML tutorial and examples in documentation.

**Risk 2: LLM Generates Confusing or Incorrect Dashboards**  
LLM misunderstands user intent and creates dashboard that doesn't match expectations. User lacks confidence in AI-generated SQL correctness.  
**Mitigation**: Assistant panel shows SQL query and sample results before creating dashboard. User can review and request changes. "Explain" button provides natural language description of what query does. Verification loop ensures SQL executes successfully before saving. Include feedback mechanism: thumbs up/down on generated dashboards.

**Risk 3: Performance Degrades with Large Dashboards**  
Dashboard with 20+ complex charts causes browser slowdown or memory issues. Users frustrated with laggy interaction.  
**Mitigation**: Warn users when creating dashboard with more than 10 charts. Implement virtualization or lazy loading for off-screen charts. Consider paginating very large dashboards into multiple views. Performance monitoring alerts team when render times exceed budgets. Recharts optimization: disable animations on charts beyond threshold.

**Risk 4: Users Unaware of Stale Data**  
Freshness indicator too subtle; users make decisions on hours-old data thinking it's current. Leads to incorrect business conclusions.  
**Mitigation**: Prominent timestamp badge on every chart, not just dashboard level. Color coding with red alert for data older than acceptable threshold. Configurable staleness warnings per dashboard type. Future: blocking warning modal if data exceeds critical age. User education: onboarding explains freshness model.

**Risk 5: Edit Conflicts and Data Loss**  
User spends 30 minutes editing dashboard, browser crashes before saving. Or two users edit same dashboard simultaneously (post-MVP concern).  
**Mitigation**: Autosave draft to browser localStorage every 30 seconds. On reload, detect draft and offer to restore. Confirmation dialog before navigation with unsaved changes. Post-MVP: implement optimistic locking or operational transforms for multi-user editing.

### **11. Acceptance Criteria (MVP)**

**Functional Criteria**  
- User can authenticate via Google SSO and access dashboard list
- Dashboard list displays all available dashboards with title and owner
- Clicking dashboard navigates to view showing all charts rendered from backend data
- Each chart displays as-of timestamp and freshness indicator
- User can initiate new dashboard via chat with natural language prompt
- Assistant generates YAML and displays preview with real data
- User can save dashboard and it persists across sessions
- Edit mode allows color changes via UI properties panel
- UI changes reflect back into in-memory YAML model
- YAML editor allows direct text editing with validation
- Save workflow shows dirty state indicator before save
- Lineage view displays graph of dashboard composition

**Performance Criteria**  
- Dashboard page loads and renders in under 3 seconds on cold cache
- Cached dashboard renders in under 500ms
- Individual chart renders in under 200ms
- Time to interactive under 3 seconds on standard broadband
- Main JavaScript bundle under 200 KB gzipped

**Usability Criteria**  
- Non-technical user can create simple dashboard via chat without YAML knowledge
- User understands data freshness from visual indicators
- Edit workflow intuitive: no training required for color/title changes
- Error messages actionable with clear next steps
- Lineage view navigable without instructions

**Demonstration Criteria**  
- Create two distinct dashboards from scratch using only chat interface
- Demonstrate UI edit changing chart color and reflecting in saved YAML
- Show YAML editor changes immediately rendering in visual view
- Navigate lineage view and explain data flow from table to dashboard

### **12. Implementation Phasing**

**MVP Completion (Current Focus)**  
Next.js app deployed to Cloud Run with SSO authentication. Application shell with three-panel layout operational. YAML-to-UI renderer supports line, bar, area, table chart types. Recharts integration complete with responsive containers. Chat interface connected to backend LLM orchestration. Save workflow with dirty state tracking functional. Lineage view renders read-only graph from backend. Freshness indicators display on all charts. Two reference dashboards demonstrating full workflow. Target completion: Week 8.

**Phase 1 Preview (Post-MVP)**  
Automatic freshness updates: Pub/Sub message from backend triggers UI banner "New data available." Dashboard list shows last refresh time and next scheduled refresh. Enhanced table previews with sorting and filtering. Basic share functionality: generate read-only link for external stakeholders. Improved performance with Memorystore-backed backend cache reducing p95 latency under 300ms. Estimated timeline: Weeks 9-12.

**Phase 2/3 Preview (Future)**  
Custom chart types beyond Recharts standard library: heatmaps, Sankey diagrams, network graphs. Templated variables: parameterize dashboards with date ranges or filter values editable in UI. Slack and Linear context panel: LLM can reference external discussions when generating dashboards. Multi-user roles: viewer, editor, admin with appropriate UI restrictions. Downloadable report mode: export dashboard as PDF or PowerPoint with static snapshots. Estimated timeline: Months 4-6.

### **12.1 Implementation Status & Task Trace (2025-10-31)**

| Area | Status | Task Reference | Notes |
|------|--------|----------------|-------|
| Phase 1 – Foundation & Setup | ✅ Complete | docs/task.md (Frontend Phase 1.1-1.3) | Monorepo, pnpm workspaces, Tailwind/ShadCN baseline landed; matches current dev workflow. |
| Phase 1.5 – Universal AI SDK Integration | 📝 Planned | docs/task.md (Frontend Phase 1.5.1-1.5.11) | Vercel AI SDK chat UI, session management, tool display, cost tracking. Depends on backend `/chat` and `/sessions` endpoints. Critical for LLM-assisted dashboard creation. |
| Phase 2 – OpenAPI Client & Auth | ✅ Complete | docs/task.md (Frontend Phase 2.1-2.4) | Generated TypeScript client + Google SSO shell finished 2025-10-29; enables authenticated data fetches. |
| Phase 3.1 – Chart Components | ✅ Complete | docs/task.md (Frontend Phase 3.1) | Core chart primitives (Line/Bar/Area/Table/KPI) implemented with monotone theme + skeletons. |
| Phase 3.2 – Dashboard Widgets | 🚧 In Progress | docs/task.md (Frontend Phase 3.2) | Layout + freshness + operational auto-refresh outstanding; ties directly to Analytical/Operational/Strategic view UX. |
| Phase 4 – Dashboard Pages & Data Hooks | 🚧 In Progress | docs/task.md (Frontend Phase 4.1-4.3) | Hooks + gallery/view wiring pending; required before E2E smoke flows pass. |
| Phase 8.1 – Datasets Explorer (Schema Browser UI) | 📝 Planned | docs/task.md (Frontend Phase 8.1) | UX spec ready (lazy tree, virtual scroll, preview panel); waiting on hooks + schema API wiring. |
| Editor & Chat Enhancements (Phase 5) | 📝 Planned | docs/task.md (Frontend Phase 5) | Builder/YAML tabs, autosave workflows queued after core dashboard pages stabilize. |
| Phase 6 – LLM Chat (Enhanced) | 📝 Planned | docs/task.md (Frontend Phase 6.1-6.4) | Builds on Phase 1.5; adds dashboard creation flow, iterative refinement, "Explain this" feature. Requires Phase 1.5 completion. |

**Outstanding follow-ups**
- Complete Phase 3.2 operational behaviours (auto-refresh cadence, alert banner) to satisfy UI PDR operational requirements.
- Ship TanStack Query hooks + gallery/view integration before layering editor/chat features.
- Implement Phase 1.5 (Universal AI SDK) before starting Phase 6 (LLM Chat) to avoid rework.
- Ensure schema browser UI consumes `/v1/schema/*` endpoints once available; reuse caching guidance from backend PDR §12.3.

### **12.2 Decision Log (Updated)**
- Adopted `@peter/api-client` generated from backend OpenAPI (docs/task.md Phase 2.1) to guarantee type parity between tiers.
- Sticking with Next.js App Router + React Server Components for authenticated routing; enables server-side session validation before data fetch.
- **Frontend as Pure Display Layer for AI**: Backend Universal AI SDK handles all LLM calls, provider selection, tool execution, and cost tracking. Frontend uses Vercel AI SDK (`ai` package) solely for streaming UX via `useChat()` hook. No direct LLM provider SDKs in frontend. All session/message storage in backend GCS, frontend hydrates from API.
- Schema Browser UI will lazy-load datasets/tables with virtual scrolling to keep DOM footprint low, aligning with zero-cost backend plan.
- **Multi-Store State Pattern**: Zustand stores split by domain (Session, Chat, Dashboard) to prevent state conflicts and enable independent hydration/invalidation cycles.

### **12.3 Schema Browser UI Snapshot**
- Left-rail tree lazily loads datasets → tables; leverages virtualized list for large inventories.
- Right-side panel shows schema (columns, types, partitioning) and preview (paginated 50-row default, up to 1000) with “Load more”.
- Cache invalidation driven from user action (refresh button) and backend TTLs (datasets 1h, tables 15m) to ensure freshness while keeping BigQuery spend at $0.

### **13. Open Questions & Assumptions**

**Questions**  
- Viewport support: how far down should we support mobile viewports? MVP assumes desktop/laptop only; mobile adaptation unclear priority.
- Dark mode default: should dark mode be default or light? User preference or system detection? Need design decision.
- Chart library lock-in: committed to Recharts or evaluate alternatives if limitations found? D3.js lower-level option with more flexibility.
- Collaboration model: eventual real-time editing or async save-and-merge workflow acceptable? Impacts state management architecture.

**Assumptions**  
- Users primarily access dashboards on desktop browsers during business hours
- Target audience comfortable with modern web applications and chat interfaces
- Browser support: latest two versions of Chrome, Firefox, Safari, Edge only
- All users have adequate bandwidth for 200 KB dashboard payloads
- Recharts covers 90% of visualization needs without custom chart types
- YAML syntax acceptable for advanced users; UI editing sufficient for majority
- React ecosystem remains stable; Next.js framework suitable for 2-3 year roadmap

---
