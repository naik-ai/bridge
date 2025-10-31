
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

**State Management**  
React Context or Zustand stores: current user session, active dashboard YAML model, dirty flag, last save timestamp, assistant conversation history. No persistence beyond session for MVP. Changes held in memory until explicit save triggers backend API call.

**Data Flow**  
Server-side rendering fetches dashboard metadata on route load. Client components request chart data from backend API. Responses cached in React Query for efficient re-renders. UI mutations update in-memory YAML model. Save action posts YAML to backend, receives confirmation, resets dirty flag.

**Styling System**  
Tailwind CSS provides utility-first styling. ShadCN components offer pre-built accessible patterns. Design tokens define spacing, colors, typography following minimal aesthetic. Light and dark modes supported via CSS variables. Custom theme variations possible without component changes.

**Chart Rendering**  
Recharts library renders all visualizations. Data arrives as arrays from backend. Chart configurations derived from YAML metadata: chart type, axes, colors, legend placement. Responsive containers handle window resizing. Loading skeletons show during fetch. Error boundaries catch rendering failures gracefully.

### **4. Data & Control Flows**

**Dashboard View Load Flow**  
User navigates to dashboard URL with slug identifier. Next.js middleware validates session cookie. Server component fetches dashboard metadata from backend API. Server pre-renders layout structure. Client component hydrates and requests chart data via GET data endpoint. Backend returns compact payloads with as-of timestamps. Client renders charts using Recharts with data props. Freshness badges display timestamps. User interacts with charts: zoom, hover for tooltips, legend toggles.

**LLM-Assisted Dashboard Creation Flow**  
User clicks "New Dashboard" button. Frontend shows chat interface with example prompts. User types natural language request describing desired visualization. Frontend sends prompt to backend orchestration endpoint. Backend coordinates LLM agent which generates YAML. Backend verifies SQL queries through execution loop. Backend returns YAML to frontend. Frontend parses YAML into in-memory model. Renderer engine transforms model into React component tree. UI displays charts with real data. User reviews and optionally requests modifications through chat. Final edit triggers save action.

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
| Phase 2 – OpenAPI Client & Auth | ✅ Complete | docs/task.md (Frontend Phase 2.1-2.4) | Generated TypeScript client + Google SSO shell finished 2025-10-29; enables authenticated data fetches. |
| Phase 3.1 – Chart Components | ✅ Complete | docs/task.md (Frontend Phase 3.1) | Core chart primitives (Line/Bar/Area/Table/KPI) implemented with monotone theme + skeletons. |
| Phase 3.2 – Dashboard Widgets | 🚧 In Progress | docs/task.md (Frontend Phase 3.2) | Layout + freshness + operational auto-refresh outstanding; ties directly to Analytical/Operational/Strategic view UX. |
| Phase 4 – Dashboard Pages & Data Hooks | 🚧 In Progress | docs/task.md (Frontend Phase 4.1-4.3) | Hooks + gallery/view wiring pending; required before E2E smoke flows pass. |
| Phase 8.1 – Datasets Explorer (Schema Browser UI) | 📝 Planned | docs/task.md (Frontend Phase 8.1) | UX spec ready (lazy tree, virtual scroll, preview panel); waiting on hooks + schema API wiring. |
| Editor & Chat Enhancements (Phases 5-6) | 📝 Planned | docs/task.md (Frontend Phases 5-6) | Builder/YAML tabs, autosave, chat workflows queued after core dashboard pages stabilize. |

**Outstanding follow-ups**
- Complete Phase 3.2 operational behaviours (auto-refresh cadence, alert banner) to satisfy UI PDR operational requirements.
- Ship TanStack Query hooks + gallery/view integration before layering editor/chat features.
- Ensure schema browser UI consumes `/v1/schema/*` endpoints once available; reuse caching guidance from backend PDR §12.3.

### **12.2 Decision Log (Updated)**
- Adopted `@peter/api-client` generated from backend OpenAPI (docs/task.md Phase 2.1) to guarantee type parity between tiers.
- Sticking with Next.js App Router + React Server Components for authenticated routing; enables server-side session validation before data fetch.
- Schema Browser UI will lazy-load datasets/tables with virtual scrolling to keep DOM footprint low, aligning with zero-cost backend plan.

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
