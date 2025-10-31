# **Dashboard Platform — Frontend UI & UX Design Review**

**Name**: Peter (after Peter Lynch)  
**Version**: 1.0 MVP  
**Date**: 2025-10-30  
**Owner**: Jay (Architect)  
**Focus**: Visual structure, page layouts, component specifications, interaction patterns, and responsive behavior

---

## 1. Problem & Goals

**Problem**  
Users need dashboard interfaces that balance information density with clarity. Current analytics tools either overwhelm with complexity or oversimplify to the point of uselessness. No single interface serves both operational monitoring and strategic analysis needs. Visual encoding often requires excessive cognitive effort to decode.

**Goals**  
- Design view types that adapt presentation to user intent: Analytical for exploration, Operational for monitoring, Strategic for executive summaries  
- Create consistent visual language using position and length as primary encoding channels to minimize decoding effort  
- Establish responsive 12-column grid system that maintains hierarchy and relationships across devices  
- Implement accessibility-first patterns with keyboard navigation and screen reader support  
- Provide clear data freshness indicators so users understand temporal context  
- Enable two-way editing between visual builder and YAML with instant preview

---

## 2. Scope & Non-Goals

**In Scope**  
- Three primary view types: Analytical, Operational, Strategic with distinct layout templates  
- Seven core pages: Login, Gallery, Dashboard View, Editor, Lineage, Datasets, Settings  
- Visual component specifications for all dashboard widgets and controls  
- Responsive grid system with mobile, tablet, and desktop breakpoints  
- Interaction patterns for dashboard creation, editing, and exploration  
- Accessibility requirements including keyboard navigation and ARIA labels  
- Performance budgets for page load and chart rendering  
- Visual prototypes that document layout hierarchy and information density expectations

**Out of Scope**  
- Custom CSS beyond ShadCN design system tokens  
- Animated transitions or micro-interactions beyond basic hover/focus states  
- Advanced data visualizations beyond standard chart types  
- Mobile-specific native app considerations  
- Print stylesheets or export formatting  
- Interactive tutorials; onboarding education handled separately

---

## 3. Design Architecture & System Foundations

### 3.1 View & Layout Model
- *Analytical*: Multi-panel exploration with deep filters, comparison tooling, default “Last 90 days” context  
- *Operational*: High-refresh dashboard with alert banner, KPI rail, 30s auto-refresh controls  
- *Strategic*: Executive summary emphasizing narrative copy, compact KPIs, minimal chrome  
- Persistent application shell—Explorer rail (navigation), workspace content, Assistant panel (LLM). Shell is omitted only on `/login`; modals reuse ShadCN dialog primitives.

### 3.2 Monotone Color Palette
The UI adheres to a strictly neutral scheme; semantic colors appear only inside data visualizations or status badges.

```
Backgrounds  : bg-primary #FFFFFF (light) / #0A0A0A (dark)
               bg-secondary #F9F9F9 / #171717
               bg-tertiary #F3F3F3 / #262626
Text         : text-primary #0A0A0A / #FAFAFA
               text-secondary #525252
               text-tertiary #737373
Border       : #E5E5E5 / #404040
Semantic     : success #10B981, warning #F59E0B, error #EF4444 (data/status use only)
Focus ring   : 2px solid #0A0A0A (light) / #FAFAFA (dark)
```

Rules: no branded accent colors for chrome; charts default to greyscale gradients with semantic accents layered only for thresholds. Hover states rely on opacity shifts, not color swaps.

### 3.3 Typography Stack
| Token | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| h1    | 32px | 600    | 1.2         | Page titles |
| h2    | 24px | 600    | 1.3         | Section headers |
| h3    | 20px | 600    | 1.4         | Subsection headers |
| h4    | 16px | 600    | 1.5         | Card headers |
| body  | 16px | 400    | 1.5         | Primary copy |
| small | 14px | 400    | 1.5         | Supporting text |
| tiny  | 12px | 400    | 1.4         | Metadata, helper text |
| kpi   | 28–32px | 600 | 1.0         | Numeric KPIs (tabular-nums) |

Font family: Inter with system fallbacks (`-apple-system`, `BlinkMacSystemFont`, `sans-serif`).

### 3.4 Spacing, Grid, and Radius
- Spacing scale: 4 / 8 / 16 / 24 / 32 / 48 / 64 px (tight → XXL).  
- Grid: 12-column responsive with gutters 16px (mobile) and 24px (desktop); max content width 1440px.  
- Breakpoints: mobile <640px, tablet 640–1024px, desktop >1024px.  
- Border radii: 4px (inputs), 8px (cards), 12px (dialogs).

### 3.5 Component & Interaction Tokens
- Components: ShadCN primitives (Buttons, Inputs, Select, Tabs, Dialog, Checkbox, Radio).  
- Charts: Recharts via shared `ChartContainer` to standardize headers, skeletons, legends, and tooltip patterns.  
- States: skeleton shimmer surfaces within 150 ms; buttons honor disabled opacity 50%; focus-visible for all interactive elements.  
- Semantic badges communicate freshness (green <1h, yellow 1–4h, red >4h, grey unknown) and confidence levels in AI flows.

---

## 4. Visual Context & Interaction Principles

- Layouts rely on spatial grouping, typographic hierarchy, and iconography to communicate importance before reading copy  
- Freshness and status information is always positioned top-left per chart to align with scanning habits  
- Modals and confirmation dialogs reuse global patterns (focus trap, Escape closes, primary button on the right)  
- Accessibility: keyboard reachability (Tab → Enter → Space), focus-ring visibility, ARIA labels added to charts/tables/menus  
- Performance budget: first meaningful paint < 3s on cold cache, CPI (chart paint interval) < 200ms per widget; skeletons displayed within 150ms

---

## 5. Chronological User Journey & Screen Action Items

The sequence below mirrors the Phase 0 onboarding wizard (12 discrete steps) followed by the core workspace experience users rely on once onboarding is complete.

### 5.1 Login & Allowlist (`/login`, OAuth callback)
- Select **Sign in with Google** → complete OAuth flow; allowlisted emails proceed, others receive inline “request access” messaging.  
- Successful auth sets secure session cookie and redirects either to the team selector (multiple teams) or onboarding home (new org).  
- Failure states keep focus on the error summary; keyboard-only navigation supported end-to-end.

### 5.2 Team Creation Wizard — Steps 1‑3 (`/teams/new`)
- **Step 1: Welcome & Team Name** – capture team name, preview slug, show checklist teaser; `Continue` gated on non-empty name.  
- **Step 2: Team Members** – paste multi-line email list, assign default role, optional “Send invites now” checkbox, duplicate detection warnings.  
- **Step 3: Team Preferences** – choose theme, timezone (auto-suggest from browser), date/number formats, currency; live preview panel reflects selections.  
- Actions: `Skip` available on each step, `Back` persists state, inline validation for email format and required choices.

### 5.3 Onboarding Home & Progress Tracker (`/onboarding`)
- Checklist card lists all 13 steps with status chips (Not Started / In Progress / Done); progress ring and ETA summary.  
- “Resume where you left off” CTA jumps into the next incomplete step; panel on the right surfaces quick links to docs and support.  
- Team owners can reset individual steps from overflow menu; analytics event `onboarding_step_reset` recorded.

### 5.4 Step 4 – Connect BigQuery (`/onboarding/connections`)
- Upload service-account JSON (drag/drop or file picker); preview client email and project ID for confirmation.  
- Run validation: dry-run `SELECT 1`, permissions check (`datasets.list`, `tables.list`, `jobs.create`); errors inline with guidance.  
- Once validated, mark step complete and expose “Add another connection” secondary action.

### 5.5 Step 5 – Dataset Discovery (`/onboarding/catalog/datasets`)
- Kick off INFORMATION_SCHEMA scan via job panel; progress percentages update as schemas/tables/columns sync.  
- Dataset table supports search, region filter, freshness color coding; selecting dataset advances to table preview step.

### 5.6 Step 6 – Table Schema Preview (`/onboarding/catalog/tables`)
- Display table list with size, row count, partition info; selecting a table opens schema + sample rows drawer.  
- “Run Sample Query” button executes dry-run to verify access; user marks the tables they intend to surface in onboarding report.

### 5.7 Step 7 – AI Dashboard Generation (`/onboarding/ai-dashboard`)
- Provide natural-language prompt (seeded with discovered datasets); toggle for including glossary + goals context.  
- Assistant streams proposed YAML, verification status, and snapshot preview; user can `Accept`, `Retry`, or `Edit in Builder`.  
- Accepted dashboards saved as drafts and referenced in completion checklist.

### 5.8 Step 8 – Business Goals Mapping (`/onboarding/goals`)
- Enter or import business goals; LLM maps each to datasets with confidence badges and reasoning notes.  
- Actions per goal: `Accept Mapping`, `Retry`, `Edit Manually`; low-confidence mappings trigger caution banner.  
- Accepted mappings stored for governance policies and onboarding report narrative.

### 5.9 Step 9 – Cost Estimation & Verification (`/onboarding/cost`)
- Show estimated bytes scanned per query + projected monthly cost; highlight assumptions (10 dashboards × 100 queries/day).  
- `Run Verification` executes dry-runs on top 5 largest tables; results list tables verified, bytes scanned, anomalies.  
- Completion criteria: verification job succeeds and user acknowledges cost summary.

### 5.10 Step 10 – Workspace Preferences (`/onboarding/preferences`)
- Review auto-generated workspace defaults (view type, timezone, theme) with the ability to tweak before graduating to Settings.  
- Example preview cards display how numbers/dates will render; “Apply to team” persists preferences for all members.

### 5.11 Step 11 – Onboarding Summary Report (`/onboarding/report-preview`)
- Generate HTML + PDF summary (executive overview, catalog stats, PII results, goals, governance recommendations, cost).  
- Provide download links, share-to-email option, and checklist of outstanding follow-ups.  
- System records `report_generated_at` timestamp for compliance.

### 5.12 Step 12 – Completion & Next Steps (`/onboarding/done`)
- Celebration screen with key stats (setup time, tables discovered, dashboards drafted).  
- CTA buttons: `Open First Dashboard`, `Invite Members`, `Go to Dashboard Gallery`, `View Documentation`.  
- Auto-redirect to gallery after 10 seconds if no action taken; onboarding wizard hidden from primary nav afterward (accessible via Settings).

### 5.14 Dashboard Gallery (`/dashboards`)
- Search/filter (owner, tags, view type) and sort (recent, alphabetical); supports pinned and recent sections.  
- “New Dashboard” launches choice modal (Chat vs Builder).  
- Card metadata: owner avatar, last updated, freshness, tag chips; hover exposes quick actions (Open, Edit, Share).

### 5.15 Dashboard View (`/dash/:slug`)
- Toggle view types (Analytical/Operational/Strategic) via segmented control; filters persist per view via URL state.  
- Global controls: date range, manual refresh, export CSV (post-MVP placeholder).  
- Each chart offers overflow menu actions (`Explain`, `View SQL`, `Open in Builder`, `View Lineage`); operational view shows alert banner + auto-refresh countdown.

### 5.16 Dashboard Editor (`/edit/:slug`)
- **Builder**: drag/drop within 12-column grid, resize handles snap to grid, property panel for metrics, formatting, theme overrides.  
- **YAML**: syntax-highlighted editor with JSON schema validation, format button, diff indicator.  
- **Preview**: live render using current YAML; `Validate` calls backend and highlights errors inline. Dirty state banner guards against navigation loss.

### 5.17 Assistant & Chat (`/assistant`)
- Chat dock (320px) or modal on smaller breakpoints; shows streaming responses with verification subtasks.  
- Supports system prompts (starter examples), markdown rendering, inline charts, and action buttons (`Apply`, `Discard`).  
- “Explain this” auto-injects chart metadata; all prompts logged with prompt hash + token usage for observability.

### 5.18 Lineage Explorer (`/lineage/:slug`)
- Directed graph with panning/zooming, layer toggles (dashboards/charts/queries/tables), and minimap.  
- Node drawer provides metadata (SQL snippet, last refreshed, upstream/downstream counts) plus buttons to open Builder or consult Assistant.

### 5.19 Schema Explorer (`/datasets`)
- Lazy-loaded tree (dataset → table → column); virtualized lists for large inventories.  
- Detail pane surfaces schema, partitioning, clustering, sample rows with pagination controls.  
- “Mark as Sensitive” button feeds back into PII module; copy-to-clipboard for column names.

### 5.20 Settings & Team Management (`/settings`)
- Personal tab: theme, density, notification preferences, passwordless session controls.  
- Team tab: manage members (invite, change role, revoke), adjust workspace defaults, configure auto-refresh cadence.  
- Security tab (post-MVP) placeholder for audit logs; for now, stores SSO info and webhook configuration.

### 5.21 Jobs & Notifications (`/jobs`)
- List of onboarding, crawl, LLM, and verification jobs with status chips, runtime, retries.  
- Detail drawer shows logs, error messages, retry button, and download links for artifacts (glossary CSV, verification results).

### 5.22 Logout
- Header avatar → `Sign Out`; server invalidates session, clears cookies, and redirects to `/login`.  
- Optional toast (“You’ve been signed out”) shown before redirect when network latency permits.

---

## 6. Interaction Patterns, Accessibility, and Visual Defaults

- **Navigation**: Explorer rail anchors “Dashboards”, “Datasets”, “Lineage”, “Jobs”, “Settings”; keyboard shortcut `Cmd/Ctrl+K` opens command palette  
- **Feedback**: All mutating actions surface toast (success/warn/error) + inline validation states  
- **Forms**: Use ShadCN `Form` + Zod validation; error summary at top for long forms  
- **Charts**: Legend toggles, hover tooltips with min-max summary, download CSV (post-MVP) placeholder  
- **Color & Typography**: Monotone base palette (HSL greys) with semantic accents; Inter typeface; headings sizes scale 1.25× ratio  
- **Accessibility**: Skip-to-content link, focus-visible overlays, proper ARIA for tabs, dialogs, charts (role="img", `aria-description`)  
- **Performance**: Don’t render assistant panel until opened; virtualization for lists >100 rows; skeletons ready under 150ms  
- **Internationalization Prep**: Date/number formats stored in preferences; copy strings centralised for future localization

---

## 7. Open Questions & Assumptions

- **Viewport support**: MVP optimized for desktop ≥1280px; tablet experience acceptable but not primary; mobile reserved for read-only future work  
- **Dark mode default**: Currently follows system preference; confirm default for enterprise rollouts  
- **Chart library**: Recharts meets MVP; revisit if heatmaps/Sankey become requirements  
- **Collaboration model**: MVP single-editor; roadmap includes optimistic locking or real-time presence  
- **Help & education**: Tooltips and inline guidance exist; broader onboarding/training handled outside UI scope

Assumptions mirror PDR baselines: modern desktop browsers (latest Chrome, Firefox, Safari, Edge), users comfortable with web apps + chat interactions, adequate bandwidth for ~200 KB payloads.

---

## 8. Decision Log (Snapshot)

- Retained three-view layout strategy after prototype testing—users clearly distinguished operational vs strategic needs  
- Operational dashboards mandate top-level alert banner + auto-refresh controls to avoid silent staleness  
- Freshness color semantics (green <1h, yellow 1–4h, red >4h, grey unknown) standardized across charts and lists  
- Schema browser adopts hierarchical tree to keep mental model consistent with BigQuery dataset → table relationships  
- Builder/YAML/Preview triad confirmed to support both low-code and power-user mental models without duplicating screens

---

This refactored UI PDR balances the original problem/architecture narrative with actionable, chronological user flows so engineering, design, and product teams can execute against clear screen-by-screen expectations. For deeper wireframes and responsive breakpoints, refer to the design system Figma source (unchanged) and the backend task list for implementation status.
