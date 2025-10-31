# **Dashboard Platform — Frontend UI & UX Design Review**

**Name**: Peter (after Peter Lynch)  
**Version**: 1.0 MVP  
**Date**: 2025-10-30  
**Owner**: Jay (Architect)  
**Focus**: Visual structure, page layouts, component specifications, interaction patterns, and responsive behavior

---

## **PDR — Frontend UI, Views & Components (MVP)**

### **1. Problem & Goals**

**Problem**  
Users need dashboard interfaces that balance information density with clarity. Current analytics tools either overwhelm with complexity or oversimplify to the point of uselessness. No single interface serves both operational monitoring and strategic analysis needs. Visual encoding often requires excessive cognitive effort to decode.

**Goals**  
- Design view types that adapt presentation to user intent: Analytical for exploration, Operational for monitoring, Strategic for executive summaries
- Create consistent visual language using position and length as primary encoding channels to minimize decoding effort
- Establish responsive 12-column grid system that maintains hierarchy and relationships across devices
- Implement accessibility-first patterns with keyboard navigation and screen reader support
- Provide clear data freshness indicators so users understand temporal context
- Enable two-way editing between visual builder and YAML with instant preview

### **2. Scope & Non-Goals**

**In Scope**  
- Three primary view types: Analytical, Operational, Strategic with distinct layout templates
- Seven core pages: Login, Gallery, Dashboard View, Editor, Lineage, Datasets, Settings
- Visual component specifications for all dashboard widgets and controls
- Responsive grid system with mobile, tablet, and desktop breakpoints
- Interaction patterns for dashboard creation, editing, and exploration
- Accessibility requirements including keyboard navigation and ARIA labels
- Performance budgets for page load and chart rendering
- Visual prototypes showing layout and component placement

**Out of Scope**  
- Custom CSS beyond ShadCN design system tokens
- Animated transitions or micro-interactions beyond basic hover/focus states
- Advanced data visualizations beyond standard chart types
- Mobile-specific native app considerations
- Print stylesheets or export formatting
- User onboarding flows or tutorial overlays

### **3. Architecture Overview**

**View Type System**  
Three presentation modes affect layout density, widget prominence, and default configurations. Same underlying YAML data; different visual emphasis.

**Analytical View**: Multi-panel exploration interface. Prominent filters and drill-down controls. Charts sized for detailed examination. Comparison tools visible. Default time range: last 90 days. Best for: ad-hoc analysis, trend investigation, cohort comparison.

**Operational View**: High-refresh monitoring interface. KPIs and status indicators above the fold. Alert banners prominent. Minimal chrome. Default time range: today or last hour. Auto-refresh indicators. Best for: real-time monitoring, incident response, operational dashboards.

**Strategic View**: Executive summary interface. Large KPI tiles with context. Narrative text blocks interspersed. Minimal interactions. Clean whitespace. Default time range: YTD or fiscal period. Best for: board presentations, strategy reviews, stakeholder updates.

**Component Hierarchy**  
Application shell provides consistent frame. Explorer rail on left for navigation. Workspace center area holds active content. Assistant panel on right for LLM interaction. All pages inherit this structure except login.

**Responsive Strategy**  
Mobile-first component design with progressive enhancement. Single column layout on mobile with stacked priority. Two-three column layouts on tablet. Full multi-column with persistent rails on desktop. Grid reflows without losing semantic relationships.

**Design System Foundation**  
ShadCN provides base component primitives: buttons, cards, dialogs, inputs, menus, tabs. Recharts provides chart components wrapped in ShadCN chart containers. Custom compositions for dashboard-specific widgets built on these foundations. Tailwind utility classes for spacing and layout.

### **4. Information Architecture & Routing**

**Route Structure**

Primary Routes:
- `/login` - Google SSO authentication handoff
- `/dashboards` - Gallery view with search and filters
- `/dash/:slug` - Dashboard display in read mode
- `/edit/:slug` - Dashboard editor with three tabs
- `/lineage/:slug` - Lineage graph visualization
- `/datasets` - Schema browser and data explorer
- `/settings` - User preferences and configuration
- `/help` - Keyboard shortcuts and documentation

**Navigation Patterns**  
Global search accessible via command palette (Cmd/Ctrl+K). Breadcrumbs show current location hierarchy. Explorer rail maintains context across page transitions. Tabs within workspace area preserve state when switching between dashboard view and editor.

**Deep Linking**  
All dashboard views support version parameter: `/dash/:slug?v=timestamp`. Filters encoded in URL query string for shareability: `/dash/:slug?date=last-90d&region=us-west`. Editor preserves last active tab: `/edit/:slug?tab=yaml`.

### **5. Page Specifications with Visual Prototypes**

---

#### **A) Login Page (`/login`)**

**Purpose**: Authenticate users via Google SSO

**Layout**: Centered card on neutral background

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│                                                            │
│                    ┌────────────────┐                      │
│                    │                │                      │
│                    │   Peter Logo   │                      │
│                    │                │                      │
│                    │ [Dashboard      │                      │
│                    │  Platform]      │                      │
│                    │                │                      │
│                    │ ┌────────────┐ │                      │
│                    │ │ Continue   │ │                      │
│                    │ │ with       │ │                      │
│                    │ │ Google     │ │                      │
│                    │ └────────────┘ │                      │
│                    │                │                      │
│                    │ Analytics and  │                      │
│                    │ insights for   │                      │
│                    │ data teams     │                      │
│                    └────────────────┘                      │
│                                                            │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Components**: Logo, heading, Google SSO button, descriptive tagline

**Interactions**: Single primary action redirects to Google OAuth flow

**Acceptance**: Successful auth redirects to `/dashboards`; failed auth shows inline error

---

#### **B) Dashboard Gallery (`/dashboards`)**

**Purpose**: Discover, search, and access dashboards

**Layout**: Grid of dashboard cards with search and filters

```
┌────────────────────────────────────────────────────────────┐
│ ☰ Explorer          Dashboards                    [User▾]  │
├─────────┬──────────────────────────────────────────────────┤
│         │                                                  │
│ [🔍]    │  [🔍 Search dashboards...]  [+ New] [↓ Filter]  │
│         │                                                  │
│ 📊 Dash │  ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│ 📁 Data │  │ Revenue    │ │ Customer   │ │ Operations │  │
│         │  │ Trends     │ │ Analytics  │ │ KPIs       │  │
│ Recent  │  │            │ │            │ │            │  │
│ • Rev   │  │ By: Sarah  │ │ By: Mike   │ │ By: Alex   │  │
│ • Ops   │  │ Updated:   │ │ Updated:   │ │ Updated:   │  │
│ • Cust  │  │ 2h ago     │ │ 5h ago     │ │ Yesterday  │  │
│         │  │            │ │            │ │            │  │
│ Tags    │  │ [Finance]  │ │ [Growth]   │ │ [Ops]      │  │
│ Finance │  │ [KPI]      │ │ [Product]  │ │ [Monitor]  │  │
│ Growth  │  └────────────┘ └────────────┘ └────────────┘  │
│ Product │                                                  │
│ Ops     │  ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│         │  │ Marketing  │ │ Sales      │ │ Product    │  │
│         │  │ Metrics    │ │ Pipeline   │ │ Usage      │  │
│         │  │ ...        │ │ ...        │ │ ...        │  │
│         │  └────────────┘ └────────────┘ └────────────┘  │
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

**Components**:
- Header: app title, global search, new dashboard button, user menu
- Left rail: Explorer tree (dashboards, datasets), recent items, tag filters
- Main area: Search input, filter dropdown, dashboard cards in responsive grid
- Dashboard card: title, owner, last updated, tags, thumbnail preview

**Interactions**:
- Click card opens `/dash/:slug`
- Search filters cards in real-time
- Filter dropdown: owner, tags, date range, view type
- New button opens modal: "Create from chat" or "Import YAML"

**Empty State**: No dashboards yet. Large CTA button: "Create your first dashboard"

**Acceptance**: Can search, filter, and open existing dashboards; create new button functional

---

#### **C) Dashboard View (`/dash/:slug`)**

**Purpose**: Display rendered dashboard with data visualizations

**Layout - Analytical View** (default):

```
┌────────────────────────────────────────────────────────────────────┐
│ ☰ Explorer      Revenue Dashboard          ▣ Analytical  [User▾]   │
├─────────┬──────────────────────────────────────────────┬────────────┤
│         │ As of: Oct 30, 10:15 AM • Next refresh: Manual │ Assistant │
│ Dashbo  │ ┌────────────────────────────────────────────┐│           │
│ • Rev   │ │ Filters: [Last 90 Days▾] [All Regions▾] [x]││ 💬 Chat   │
│ • Ops   │ └────────────────────────────────────────────┘│           │
│ • Cust  │                                                │ "Explain  │
│         │ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  │  this     │
│ Lineage │ │ $2.4M  │ │ 12.3K  │ │ 89%    │ │ $847   │  │  chart"   │
│ [View]  │ │ Revenue│ │ Orders │ │ Uptime │ │ AOV    │  │           │
│         │ │ ↑ 15%  │ │ ↓ 3%   │ │ → 0%   │ │ ↑ 8%   │  │ Timeline  │
│ Explain │ └────────┘ └────────┘ └────────┘ └────────┘  │ • Created │
│ [Start] │                                                │   10:12   │
│         │ ┌──────────────────────┐ ┌─────────────────┐  │ • Edited  │
│         │ │ Revenue Trend        │ │ Regional Mix    │  │   10:14   │
│         │ │                      │ │                 │  │           │
│         │ │      ╱╲    ╱╲        │ │  ▆ West  45%    │  │ [Refresh] │
│         │ │     ╱  ╲  ╱  ╲       │ │  ▅ East  30%    │  │           │
│         │ │    ╱    ╲╱    ╲      │ │  ▃ South 15%    │  │           │
│         │ │ ──╱──────────────╲── │ │  ▂ North 10%    │  │           │
│         │ │   Aug  Sep  Oct      │ │                 │  │           │
│         │ │                  [⋮] │ │             [⋮] │  │           │
│         │ └──────────────────────┘ └─────────────────┘  │           │
│         │                                                │           │
│         │ ┌─────────────────────────────────────────┐   │           │
│         │ │ Top Products by Revenue                 │   │           │
│         │ │ ┌─────────┬────────┬────────┬─────────┐│   │           │
│         │ │ │Product  │ Rev    │ Orders │ Growth ↓││   │           │
│         │ │ ├─────────┼────────┼────────┼─────────┤│   │           │
│         │ │ │Widget A │ $845K  │ 1.2K   │ +23%    ││   │           │
│         │ │ │Gadget B │ $720K  │ 980    │ +18%    ││   │           │
│         │ │ │Thing C  │ $612K  │ 1.4K   │ +12%    ││   │           │
│         │ │ └─────────┴────────┴────────┴─────────┘│   │           │
│         │ │                                     [⋮] │   │           │
│         │ └─────────────────────────────────────────┘   │           │
└─────────┴──────────────────────────────────────────────┴────────────┘
```

**Layout - Operational View**:

```
┌────────────────────────────────────────────────────────────────────┐
│ ☰ Explorer      Operations KPIs           ▣ Operational  [User▾]   │
├─────────┬──────────────────────────────────────────────┬────────────┤
│         │ ⚠️ 2 Alerts Active • As of: Oct 30, 10:15 AM  │ Assistant │
│ Dashbo  │ Auto-refresh: 30s                             │           │
│ • Rev   │                                                │ Status:   │
│ • Ops   │ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  │ All OK    │
│ • Cust  │ │ 98.9%  │ │ 234ms  │ │ 1.2K/s │ │ $4.2K  │  │           │
│         │ │ Uptime │ │ P95    │ │ QPS    │ │ /hour  │  │ Alerts:   │
│         │ │ 🟢      │ │ 🟡     │ │ 🟢     │ │ 🟢     │  │ • High    │
│         │ └────────┘ └────────┘ └────────┘ └────────┘  │   latency │
│         │                                                │ • Cache   │
│         │ ┌──────────────────────────────────────────┐  │   miss    │
│         │ │ Error Rate (Last Hour)                   │  │           │
│         │ │                                          │  │           │
│         │ │  ────────────────────────────────────── │  │           │
│         │ │              Reference: 0.1%             │  │           │
│         │ └──────────────────────────────────────────┘  │           │
│         │                                                │           │
│         │ ┌──────────────┐ ┌──────────────┐            │           │
│         │ │ Active Users │ │ Queue Depth  │            │           │
│         │ │   ╱╲╱╲╱╲     │ │    ─╲╱╲─     │            │           │
│         │ └──────────────┘ └──────────────┘            │           │
└─────────┴──────────────────────────────────────────────┴────────────┘
```

**Layout - Strategic View**:

```
┌────────────────────────────────────────────────────────────────────┐
│ ☰ Explorer      Q3 Business Review        ▣ Strategic   [User▾]   │
├─────────┬──────────────────────────────────────────────────────────┤
│         │ As of: Sep 30, 2025 • Q3 FY2025                          │
│ Dashbo  │                                                          │
│ • Q3    │ ┌────────────────┐ ┌────────────────┐ ┌──────────────┐ │
│ • Q2    │ │   $12.4M       │ │   34.2K        │ │   $363       │ │
│ • Q1    │ │   Quarterly    │ │   New          │ │   Customer   │ │
│         │ │   Revenue      │ │   Customers    │ │   LTV        │ │
│         │ │   ↑ 23% YoY    │ │   ↑ 18% YoY    │ │   ↑ 12% YoY  │ │
│         │ └────────────────┘ └────────────────┘ └──────────────┘ │
│         │                                                          │
│         │ Narrative: Q3 Performance Highlights                    │
│         │ ─────────────────────────────────────────                │
│         │ Revenue exceeded targets by 8%, driven primarily by      │
│         │ enterprise segment growth. Customer acquisition cost     │
│         │ decreased 15% while maintaining conversion quality.      │
│         │                                                          │
│         │ ┌──────────────────────────────────────────────────┐   │
│         │ │ Revenue Growth Trajectory                        │   │
│         │ │                                            ╱     │   │
│         │ │                                      ╱╲  ╱      │   │
│         │ │                                ╱╲  ╱  ╲╱       │   │
│         │ │                          ╱╲  ╱  ╲╱            │   │
│         │ │ ─────────────────────────────────────────────  │   │
│         │ │   Q1      Q2      Q3      Q4 (Proj)           │   │
│         │ └──────────────────────────────────────────────────┘   │
│         │                                                          │
│         │ Key Initiatives for Q4                                   │
│         │ • Expand enterprise sales team (+5 AEs)                 │
│         │ • Launch new product tier                               │
│         │ • Optimize acquisition funnel (target: -20% CAC)        │
└─────────┴──────────────────────────────────────────────────────────┘
```

**Components**:
- Header: title, view type toggle, freshness timestamp, user menu
- Filters row: date range, segment selectors, active filter chips with remove
- KPI tiles: large value, label, delta with direction indicator, optional sparkline
- Charts: title bar with kebab menu (⋮), Recharts visualization, axis labels
- Tables: column headers with sort indicators, rows with formatted values
- Text blocks: markdown-formatted narrative content (Strategic view)
- Alert banner: status indicator, message, dismiss action

**Interactions**:
- View type toggle changes layout template and density
- Filter changes update URL params and refresh all widgets
- Chart hover shows tooltip with detailed values
- Chart kebab menu: "Explain in chat", "View SQL", "View lineage"
- Table column headers toggle sort order
- KPI tiles click to open drill-down (future)

**Freshness Indicators**:
- Global: "As of Oct 30, 10:15 AM" in header
- Per-card: "Source: revenue_daily_mv (p2025-10-30)" in footer
- Color coding: green (<1h), yellow (1-4h), red (>4h), gray (unknown)

**Acceptance**: All three view types render correctly; filters apply to all widgets; charts interactive with tooltips; freshness visible

---

#### **D) Dashboard Editor (`/edit/:slug`)**

**Purpose**: Edit dashboard structure, charts, and YAML

**Layout**: Three-tab interface with split panels

**Tab 1 - Builder (Visual Editor)**:

```
┌────────────────────────────────────────────────────────────────────┐
│ ☰ Explorer      Edit: Revenue Dashboard               [User▾]      │
├─────────┬──────────────────────────────────────────────────────────┤
│         │ [Builder] [YAML] [Preview]              ⚠️ Unsaved changes│
│ Dashbo  │ ┌────────────────────────────────────┐ ┌──────────────┐ │
│ • Rev   │ │                                    │ │ Properties   │ │
│ • Ops   │ │  ┌────────────┐   Selected:        │ │              │ │
│         │ │  │ Revenue    │   Revenue Trend    │ │ Chart Type   │ │
│ Actions │ │  │ Trend      │◄──────────────────────│ [Line ▾]    │ │
│ • Save  │ │  │            │                    │ │              │ │
│ • Valid │ │  │  Chart     │                    │ │ X Axis       │ │
│ • Test  │ │  │            │                    │ │ [date ▾]     │ │
│         │ │  └────────────┘                    │ │              │ │
│         │ │                                    │ │ Y Axis       │ │
│         │ │  ┌────────┐ ┌────────┐            │ │ [revenue ▾]  │ │
│         │ │  │ KPI    │ │ KPI    │            │ │              │ │
│         │ │  │        │ │        │            │ │ Series       │ │
│         │ │  └────────┘ └────────┘            │ │ [region ▾]   │ │
│         │ │                                    │ │              │ │
│         │ │  [+ Add Widget]                   │ │ Color        │ │
│         │ │                                    │ │ [🎨 Blue ]   │ │
│         │ │                                    │ │              │ │
│         │ │                                    │ │ Size         │ │
│         │ │                                    │ │ ( ) S        │ │
│         │ │                                    │ │ (•) M        │ │
│         │ │                                    │ │ ( ) L        │ │
│         │ │                                    │ │ ( ) XL       │ │
│         │ │                                    │ │              │ │
│         │ │                                    │ │ [Delete]     │ │
│         │ └────────────────────────────────────┘ └──────────────┘ │
│         │                                                          │
│         │ [Cancel] [Validate] [Save Dashboard]                    │
└─────────┴──────────────────────────────────────────────────────────┘
```

**Tab 2 - YAML Editor**:

```
┌────────────────────────────────────────────────────────────────────┐
│ ☰ Explorer      Edit: Revenue Dashboard               [User▾]      │
├─────────┬──────────────────────────────────────────────────────────┤
│         │ [Builder] [YAML] [Preview]              ⚠️ Unsaved changes│
│ Dashbo  │ ┌──────────────────────────────────────────────────────┐ │
│ • Rev   │ │  1  version: 0                                       │ │
│ • Ops   │ │  2  kind: dashboard                                  │ │
│         │ │  3  slug: revenue-dashboard                          │ │
│ Valida  │ │  4  title: "Revenue Dashboard"                       │ │
│ ✓ Valid │ │  5  owner: sarah@company.com                         │ │
│         │ │  6  layout:                                          │ │
│ Errors  │ │  7    - id: rev_trend                                │ │
│ (none)  │ │  8      type: chart                                  │ │
│         │ │  9      chart: line                                  │ │
│         │ │ 10      query_ref: q_revenue                         │ │
│         │ │ 11      style:                                       │ │
│         │ │ 12        color: primary                             │ │
│         │ │ 13        size: medium                               │ │
│         │ │ 14  queries:                                         │ │
│         │ │ 15    - id: q_revenue                                │ │
│         │ │ 16      warehouse: bigquery                          │ │
│         │ │ 17      sql: |                                       │ │
│         │ │ 18        SELECT date, revenue                       │ │
│         │ │ 19        FROM mart.revenue_daily                    │ │
│         │ │ 20        WHERE date >= DATE_SUB(CURRENT_DATE(), ... │ │
│         │ │ 21                                                   │ │
│         │ │ ...                                                  │ │
│         │ │                                                      │ │
│         │ │                                                      │ │
│         │ └──────────────────────────────────────────────────────┘ │
│         │                                                          │
│         │ [Format] [Validate] [Save Dashboard]                    │
└─────────┴──────────────────────────────────────────────────────────┘
```

**Tab 3 - Preview**:

```
┌────────────────────────────────────────────────────────────────────┐
│ ☰ Explorer      Edit: Revenue Dashboard               [User▾]      │
├─────────┬──────────────────────────────────────────────────────────┤
│         │ [Builder] [YAML] [Preview]              ⚠️ Unsaved changes│
│ Dashbo  │                                                          │
│ • Rev   │ Preview Mode (uses live data)                            │
│ • Ops   │ ┌────────────────────────────────────────────────────┐  │
│         │ │ Revenue Dashboard                                  │  │
│ Info    │ │                                                    │  │
│ Preview │ │ ┌────────┐ ┌────────┐                             │  │
│ uses    │ │ │ $2.4M  │ │ 12.3K  │                             │  │
│ real    │ │ │Revenue │ │ Orders │                             │  │
│ data    │ │ └────────┘ └────────┘                             │  │
│         │ │                                                    │  │
│         │ │ ┌──────────────────────┐                          │  │
│         │ │ │ Revenue Trend        │                          │  │
│         │ │ │      ╱╲    ╱╲        │                          │  │
│         │ │ │     ╱  ╲  ╱  ╲       │                          │  │
│         │ │ │ ───╱────╲╱────╲─────│                          │  │
│         │ │ └──────────────────────┘                          │  │
│         │ └────────────────────────────────────────────────────┘  │
│         │                                                          │
│         │ [← Back to Editor] [Save Dashboard]                     │
└─────────┴──────────────────────────────────────────────────────────┘
```

**Components**:
- Tab navigation: Builder, YAML, Preview
- Builder tab: canvas area with widget outlines, properties panel
- YAML tab: code editor with line numbers, syntax highlighting, validation status
- Preview tab: full rendered dashboard with live data
- Action buttons: Cancel, Validate, Save
- Dirty state banner: persistent when changes unsaved

**Interactions**:
- Builder: click widget to select, drag to reposition (future), properties panel updates
- Properties: change type/color/size updates canvas preview immediately
- YAML: edit text, validation runs on debounce, errors highlighted inline
- Preview: renders full dashboard, allows interaction testing
- Save: validates YAML, posts to backend, clears dirty state
- Navigate away with unsaved changes: confirmation dialog

**Validation States**:
- Valid: green checkmark in sidebar
- Invalid: red X with error count, errors listed, line numbers clickable
- Validating: spinner indicator

**Acceptance**: Can edit charts visually in Builder; changes reflect in YAML tab; Preview shows live rendering; Save persists changes

---

#### **E) Lineage View (`/lineage/:slug`)**

**Purpose**: Visualize data flow from source tables to dashboard

**Layout**: Interactive graph with expandable nodes

```
┌────────────────────────────────────────────────────────────────────┐
│ ☰ Explorer      Lineage: Revenue Dashboard            [User▾]      │
├─────────┬──────────────────────────────────────────────┬───────────┤
│         │                                              │ Metadata  │
│ Dashbo  │ [🔍 Search nodes...]        [⟲ Refresh]     │           │
│ • Rev   │                                              │ Selected: │
│ • Ops   │        ┌─────────────────┐                  │           │
│         │        │   Revenue       │                  │ Query:    │
│ Layers  │        │   Dashboard     │                  │ q_revenue │
│ ☑ Dash  │        └────────┬────────┘                  │           │
│ ☑ Chart │                 │                            │ Type:     │
│ ☑ Query │        ┌────────┴────────┐                  │ BigQuery  │
│ ☑ Table │        │                 │                  │           │
│         │   ┌────▼─────┐     ┌─────▼────┐            │ Scans:    │
│ Legend  │   │ Revenue  │     │ Orders   │            │ ~250MB    │
│ 🟦 Dash │   │ Trend    │     │ Count    │            │           │
│ 🟩 Chart│   │ Chart    │     │ KPI      │            │ SQL:      │
│ 🟨 Query│   └────┬─────┘     └─────┬────┘            │ SELECT    │
│ 🟧 Table│        │                 │                  │ date,     │
│         │   ┌────▼──────┐    ┌─────▼─────┐           │ revenue   │
│ Actions │   │ q_revenue │    │ q_orders  │           │ FROM      │
│ [Expand │   │           │    │           │           │ mart.rev  │
│  All]   │   └─────┬─────┘    └─────┬─────┘           │ ...       │
│         │         │                │                  │           │
│ [Collap │    ┌────▼────┐      ┌────▼────┐            │ [View SQL]│
│  All]   │    │ revenue │      │ orders  │            │ [Explain] │
│         │    │ _daily  │      │ _daily  │            │ [Open in  │
│         │    │ _mv     │      │ _mv     │            │  Builder] │
│         │    └─────────┘      └─────────┘            │           │
│         │                                              │           │
│         │                                              │           │
└─────────┴──────────────────────────────────────────────┴───────────┘
```

**Components**:
- Graph canvas: force-directed or hierarchical layout
- Nodes: color-coded by type (dashboard, chart, query, table)
- Edges: directional arrows showing data flow
- Search input: filter nodes by name or ID
- Layer toggles: show/hide node types
- Metadata panel: details for selected node
- Action buttons: Expand All, Collapse All, Refresh

**Interactions**:
- Click node: select and show metadata panel
- Double-click node: expand/collapse children
- Drag node: reposition (layout adjusts)
- Search: highlight matching nodes
- "Open in Builder" button: navigate to `/edit/:slug` with chart focused
- "Explain" button: open Assistant with node context

**Node Types**:
- Dashboard (blue rectangle): top-level container
- Chart (green rounded): visualization widget
- Query (yellow oval): SQL query definition
- Table (orange cylinder): BigQuery table/view/MV

**Metadata Panel Content**:
- Node name and type
- Query: SQL preview, bytes scanned, execution time
- Table: schema snippet, partition info, last updated, row count
- Chart: chart type, data source reference

**Acceptance**: Graph loads and displays all nodes; click interaction shows metadata; search filters correctly; expand/collapse works

---

#### **F) Datasets Explorer (`/datasets`)**

**Purpose**: Browse BigQuery schema and preview table contents

**Layout**: Three-panel browser with tree, schema, and preview

```
┌────────────────────────────────────────────────────────────────────┐
│ ☰ Explorer      Datasets Explorer                      [User▾]     │
├─────────┬──────────────────────┬─────────────────────────┬─────────┤
│         │                      │                         │ Preview │
│ Dashbo  │ Projects & Datasets  │ Table Schema            │         │
│ • Rev   │                      │                         │ orders  │
│ • Ops   │ [🔍 Search...]       │ 📊 orders_daily         │ _daily  │
│         │                      │                         │         │
│ 📁 Proj │ ▼ 📂 my-project     │ Columns (8)             │ Showing │
│ ▾ Stage │   ▼ 📂 raw          │ ┌──────────┬────────┐  │ first   │
│ ▾ Mart  │     📊 events       │ │ Name     │ Type   │  │ 100 rows│
│ ▾ Analyt│     📊 users        │ ├──────────┼────────┤  │         │
│         │     📊 orders       │ │ order_id │ STRING │  │ ┌──────┐│
│ Refresh │   ▼ 📂 staging      │ │ date     │ DATE   │  │ │ ID   ││
│ [⟲]    │     📊 clean_events │ │ customer │ STRING │  │ │ 1001 ││
│         │   ▼ 📂 mart         │ │ amount   │ FLOAT  │  │ │ 1002 ││
│         │     📊 revenue_daily│ │ status   │ STRING │  │ │ 1003 ││
│ Filters │  ▸  📊 orders_daily◄│ │ region   │ STRING │  │ │ ...  ││
│ 🔍 Name │     📊 customer_ltv │ │ ...      │ ...    │  │ └──────┘│
│ 🏷️ Tags │   ▼ 📂 analytics    │ └──────────┴────────┘  │         │
│         │     📊 user_cohorts │                         │         │
│         │     📊 churn_model  │ Partitioning            │ [Load   │
│         │                      │ • Field: date           │  More]  │
│         │                      │ • Type: DAY             │         │
│         │                      │                         │         │
│         │                      │ Clustering              │         │
│         │                      │ • region, status        │         │
│         │                      │                         │         │
│         │                      │ Last Modified           │         │
│         │                      │ Oct 30, 6:15 AM         │         │
│         │                      │                         │         │
│         │                      │ [Preview Full Schema]   │         │
└─────────┴──────────────────────┴─────────────────────────┴─────────┘
```

**Components**:
- Left panel: collapsible tree (projects > datasets > tables)
- Middle panel: selected table schema, columns, partitioning, clustering
- Right panel: data preview (first 100 rows, limited columns)
- Search: filter tree by table name
- Refresh button: reload metadata

**Interactions**:
- Click table in tree: load schema and preview
- Expand/collapse folders in tree
- Click column name: copy to clipboard
- Preview "Load More": fetch next page (capped at 500 rows total)
- Preview table is read-only, no editing

**Schema Information Displayed**:
- Column names and types
- Partition field and type
- Clustering columns
- Last modified timestamp
- Table description (if available)

**Acceptance**: Can browse BigQuery datasets; select table shows schema; preview loads sample rows; search filters tree

---

#### **G) Settings (`/settings`)**

**Purpose**: Configure user preferences and application behavior

**Layout**: Tabbed sections for different setting categories

```
┌────────────────────────────────────────────────────────────────────┐
│ ☰ Explorer      Settings                               [User▾]     │
├─────────┬──────────────────────────────────────────────────────────┤
│         │                                                          │
│ Dashbo  │ [Appearance] [Preferences] [Account]                    │
│ • Rev   │                                                          │
│ • Ops   │ ┌────────────────────────────────────────────────────┐ │
│         │ │ Appearance                                         │ │
│ Quick   │ │                                                    │ │
│ Links   │ │ Theme                                              │ │
│ • Theme │ │ ( ) Light                                          │ │
│ • Date  │ │ (•) Dark                                           │ │
│ • Numbe │ │ ( ) System (matches OS preference)                │ │
│         │ │                                                    │ │
│         │ │ Density                                            │ │
│         │ │ ( ) Comfortable                                    │ │
│         │ │ (•) Compact                                        │ │
│         │ │                                                    │ │
│         │ │ ─────────────────────────────────────────────────  │ │
│         │ │                                                    │ │
│         │ │ Preferences                                        │ │
│         │ │                                                    │ │
│         │ │ Default View Type                                  │ │
│         │ │ [Analytical ▾]                                     │ │
│         │ │                                                    │ │
│         │ │ Date Format                                        │ │
│         │ │ [YYYY-MM-DD ▾]                                     │ │
│         │ │                                                    │ │
│         │ │ Time Zone                                          │ │
│         │ │ [Asia/Kolkata (IST) ▾]                             │ │
│         │ │                                                    │ │
│         │ │ Number Format                                      │ │
│         │ │ [1,234.56 ▾]                                       │ │
│         │ │                                                    │ │
│         │ │ ─────────────────────────────────────────────────  │ │
│         │ │                                                    │ │
│         │ │ Account                                            │ │
│         │ │                                                    │ │
│         │ │ Email: sarah@company.com                           │ │
│         │ │ Organization: Acme Corp                            │ │
│         │ │ Role: Editor                                       │ │
│         │ │                                                    │ │
│         │ │ [Sign Out]                                         │ │
│         │ └────────────────────────────────────────────────────┘ │
│         │                                                          │
│         │                             [Save Changes]              │
└─────────┴──────────────────────────────────────────────────────────┘
```

**Components**:
- Tab navigation: Appearance, Preferences, Account
- Radio groups for mutually exclusive options
- Dropdowns for select options
- Account information display (read-only)
- Save button (only enabled when changes made)

**Settings Available**:

**Appearance Tab**:
- Theme: Light, Dark, System
- Density: Comfortable, Compact

**Preferences Tab**:
- Default view type: Analytical, Operational, Strategic
- Date format: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY
- Time zone: searchable dropdown
- Number format: 1,234.56 vs 1.234,56

**Account Tab**:
- Email (read-only)
- Organization (read-only)
- Role (read-only)
- Sign Out button

**Interactions**:
- Change any setting: Save button enables
- Click Save: persist to backend, reload UI with new settings
- Sign Out: clear session, redirect to login

**Acceptance**: Can change theme and see immediate UI update; date/number format changes reflect in dashboards; sign out works

---

#### **H) Help (`/help`)**

**Purpose**: Keyboard shortcuts and quick reference

**Layout**: Searchable documentation with categories

```
┌────────────────────────────────────────────────────────────────────┐
│ ☰ Explorer      Help & Shortcuts                       [User▾]     │
├─────────┬──────────────────────────────────────────────────────────┤
│         │                                                          │
│ Dashbo  │ [🔍 Search help...]                                      │
│ • Rev   │                                                          │
│ • Ops   │ Keyboard Shortcuts                                       │
│         │                                                          │
│ Topics  │ Navigation                                               │
│ • Short │ ┌──────────────────────────────────────────────────┐   │
│ • Dashb │ │ Cmd/Ctrl + K        Open command palette         │   │
│ • Chart │ │ Cmd/Ctrl + P        Quick search dashboards      │   │
│ • Editor│ │ Cmd/Ctrl + B        Toggle left rail             │   │
│ • Lines │ │ Cmd/Ctrl + /        Toggle assistant panel       │   │
│         │ └──────────────────────────────────────────────────┘   │
│         │                                                          │
│         │ Editor                                                   │
│         │ ┌──────────────────────────────────────────────────┐   │
│         │ │ Cmd/Ctrl + S        Save dashboard               │   │
│         │ │ Cmd/Ctrl + Z        Undo                         │   │
│         │ │ Cmd/Ctrl + Shift+Z  Redo                         │   │
│         │ │ Cmd/Ctrl + F        Find in YAML                 │   │
│         │ │ Delete              Delete selected widget       │   │
│         │ └──────────────────────────────────────────────────┘   │
│         │                                                          │
│         │ Dashboard View                                           │
│         │ ┌──────────────────────────────────────────────────┐   │
│         │ │ R                   Refresh dashboard            │   │
│         │ │ E                   Enter edit mode              │   │
│         │ │ L                   Open lineage view            │   │
│         │ │ ?                   Show this help               │   │
│         │ └──────────────────────────────────────────────────┘   │
│         │                                                          │
│         │ Working with Dashboards                                  │
│         │ • Creating: Use "New Dashboard" and describe in chat    │
│         │ • Editing: Visual builder or YAML editor                │
│         │ • Sharing: Copy URL from address bar (future: share btn)│
│         │                                                          │
│         │ Understanding Freshness                                  │
│         │ • Green badge: Data < 1 hour old                        │
│         │ • Yellow badge: Data 1-4 hours old                      │
│         │ • Red badge: Data > 4 hours old                         │
│         │ • Manual refresh: Click refresh button                  │
└─────────┴──────────────────────────────────────────────────────────┘
```

**Components**:
- Search input: filter help topics
- Category sections: collapsible accordion
- Shortcut tables: key combination + description
- Topic paragraphs: concise explanations

**Interactions**:
- Search filters content in real-time
- Click category to expand/collapse
- Click shortcut to copy to clipboard
- Press ? key from anywhere to open help

**Acceptance**: Help content searchable; shortcuts documented and work as described

---

### **6. Component Specifications**

**Base Components (from ShadCN)**

All UI elements built on ShadCN primitives for consistency:

**Buttons**:
- Primary: solid background, high contrast
- Secondary: outline style
- Ghost: transparent, hover background
- Sizes: small (32px), medium (40px), large (48px)
- States: default, hover, active, disabled

**Cards**:
- Container with border, padding, rounded corners
- Header section: title, optional actions
- Body: main content area
- Footer: metadata or secondary actions

**Inputs**:
- Text input: border, focus ring, error state
- Select dropdown: searchable when many options
- Date picker: calendar popup
- Multi-select: chips with remove

**Navigation**:
- Tabs: underlined active state
- Breadcrumbs: clickable path with separators
- Tree view: expandable folders

**Feedback**:
- Toast: bottom-right notification, auto-dismiss
- Dialog: modal overlay, focused interaction
- Tooltip: hover explanation, arrow pointer
- Skeleton: loading placeholder with shimmer

**Dashboard-Specific Components**

**KPI Tile**:
- Large value: 24-32px font, semibold
- Label: 14px, muted color, below value
- Delta: color-coded (green ↑, red ↓, gray →), percentage
- Optional sparkline: small line chart, 60px tall
- Size: S (1/4 width), M (1/3), L (1/2), XL (full)

**Chart Container (ShadCN Chart wrapper)**:
- Header: title (16px semibold), kebab menu
- Recharts canvas: responsive container
- Legend: horizontal below or vertical right
- Tooltip: follows cursor, shows all series
- Footer: as-of timestamp, source reference

**Table Widget**:
- Sticky header: remains visible on scroll
- Sortable columns: click header toggles asc/desc
- Compact row height: 36px
- Zebra striping: alternating subtle background
- Hover: highlight row
- No pagination in MVP: scroll or limit rows

**Filter Controls**:
- Date range: preset options (Last 7d, 30d, 90d, YTD) + custom
- Multi-select: dropdown with search, selected chips
- Active filters row: chips with X to remove
- Reset all: clear button

**Assistant Panel**:
- Chat thread: messages alternating left/right
- User message: right-aligned, primary color background
- Assistant message: left-aligned, secondary background
- SQL preview: collapsible code block with syntax highlight
- Action buttons: "Apply patch", "Explain more"

**Lineage Graph Nodes**:
- Dashboard: blue rectangle, 120x60px
- Chart: green rounded rectangle, 100x50px
- Query: yellow oval, 100x40px
- Table: orange cylinder, 100x50px
- Selected: thicker border, shadow

**Validation Message**:
- Error: red icon, error text, line number link
- Warning: yellow icon, warning text
- Success: green icon, success text
- Inline in YAML editor: squiggly underline

### **7. Interaction Patterns**

**Primary User Flows**

**Flow 1: Create Dashboard from Natural Language**:
1. User clicks "New Dashboard" button in gallery
2. Modal opens with chat interface
3. User types: "Show me revenue by region for last quarter"
4. Backend processes request (5-10 seconds)
5. Assistant shows progress: "Generating SQL... Verifying..."
6. Preview appears in modal with rendered charts
7. User reviews and clicks "Create Dashboard"
8. Prompted for name and slug
9. Dashboard saves and redirects to view mode

**Flow 2: Edit Chart Color Visually**:
1. User opens dashboard in view mode
2. Clicks "Edit" button in header
3. Editor opens in Builder tab
4. User clicks chart widget to select
5. Properties panel shows current settings
6. User clicks color picker
7. Selects new color from palette
8. Chart updates immediately in canvas
9. Dirty state banner appears
10. User clicks "Save Dashboard"
11. Backend validates and persists YAML
12. Success toast appears
13. User clicks "View" to see published changes

**Flow 3: Iterative SQL Refinement**:
1. User edits dashboard in YAML tab
2. Modifies SQL query text
3. Syntax validation runs on debounce
4. User clicks "Validate" button
5. Backend executes SQL sample (limited rows)
6. Results appear in panel: schema, sample data, stats
7. User sees issue (e.g., missing column)
8. User fixes SQL and clicks Validate again
9. New results look correct
10. User clicks "Save Dashboard"

**Flow 4: Explore Lineage**:
1. User viewing dashboard clicks "View Lineage" button
2. Lineage graph loads in new route
3. User sees dashboard node at top
4. User clicks chart node to expand
5. Query node appears
6. User clicks query node
7. Metadata panel shows SQL and stats
8. User clicks table node at bottom
9. Metadata shows schema and freshness
10. User clicks "Explain in Chat"
11. Assistant panel opens with context
12. LLM explains data flow

**Secondary Interactions**

**Keyboard Navigation**:
- Tab key moves focus through interactive elements
- Enter activates buttons and links
- Arrow keys navigate tree views and lists
- Escape closes modals and dropdowns
- Cmd/Ctrl+K opens command palette

**Hover States**:
- Charts: tooltip shows data point values
- Tables: highlight row on hover
- Buttons: subtle background change
- Links: underline appears

**Focus States**:
- Visible focus ring: 2px solid, high contrast
- Focus skips hidden elements
- Focus returns to trigger after modal close

**Error Recovery**:
- Invalid YAML: inline diagnostics with line numbers
- Failed save: toast with error message and retry button
- Network timeout: banner with "Try again" action
- Missing data: empty state with explanation

### **8. Responsive Behavior**

**Breakpoint Strategy**

Breakpoints based on content needs, not device types:

- **Mobile** (< 640px): Single column, stacked layout
- **Tablet** (640px - 1024px): 2-3 columns, simplified controls
- **Desktop** (1024px+): Full multi-column with persistent rails

**Layout Adaptations**

**Mobile (< 640px)**:
- Left rail collapses to hamburger menu
- Right panel hidden by default, overlay when opened
- Dashboard grid: 1 column, full width widgets
- KPI tiles: 2 per row maximum
- Charts: full width, simplified legends
- Tables: horizontal scroll, fewer columns visible
- Filters: drawer overlay instead of inline

**Tablet (640px - 1024px)**:
- Left rail: collapsible, overlay when open
- Right panel: collapsible, takes space when open
- Dashboard grid: 2 columns
- KPI tiles: 2-3 per row
- Charts: half or full width
- Tables: more columns visible, still scrollable

**Desktop (1024px+)**:
- Left rail: persistent, 240px wide
- Right panel: persistent or collapsible, 320px wide
- Dashboard grid: 3-4 columns
- KPI tiles: 4 per row
- Charts: flexible sizing (S/M/L/XL)
- Tables: full column visibility

**Responsive Component Adjustments**

**KPI Tile**:
- Mobile: value 24px, stacked layout
- Tablet: value 28px, inline delta
- Desktop: value 32px, sparkline visible

**Chart**:
- Mobile: legend below chart, simplified
- Tablet: legend below chart
- Desktop: legend right or below based on size

**Table**:
- Mobile: show 2-3 essential columns, scroll horizontally
- Tablet: show 4-5 columns
- Desktop: show all columns with comfortable spacing

**Navigation**:
- Mobile: bottom tab bar for main sections
- Tablet: top tabs with icon + label
- Desktop: full navigation rails

### **9. Accessibility Requirements**

**Keyboard Navigation**

All interactive elements reachable via Tab:
- Buttons, links, inputs, selects
- Chart hover triggers (on Enter)
- Table rows (arrow keys)
- Tree view (arrow keys expand/collapse)
- Modal dialogs (Escape to close)

Focus management:
- Visible focus indicators (2px ring)
- Focus trap in modals
- Focus returns after modal close
- Skip to main content link

**Screen Reader Support**

ARIA labels and roles:
- Charts: `role="img"` with `aria-label` describing content
- Tables: proper `th` with scope, `caption` for context
- Buttons: `aria-label` when icon-only
- Status messages: `role="status"` for live updates
- Form fields: associated `label` elements

Semantic HTML:
- Proper heading hierarchy (h1 > h2 > h3)
- Lists use `ul`/`ol` with `li`
- Navigation uses `nav` landmark
- Main content in `main` landmark

**Visual Accessibility**

Color contrast:
- Text: minimum 4.5:1 for normal, 3:1 for large
- Interactive elements: 3:1 against background
- Status indicators: don't rely on color alone

Text sizing:
- Base font: 16px
- Scalable with browser zoom up to 200%
- No fixed pixel heights that clip text

Motion:
- Respect `prefers-reduced-motion`
- Disable animations when user preference set
- Provide alternative static indicators

**Chart Accessibility**

- Data table alternative available
- Keyboard navigation through data points
- Color patterns (not just color) for series
- High contrast mode support

### **10. Performance & Quality Standards**

**Page Load Targets**

- Dashboard gallery: < 1 second first paint
- Dashboard view (cold): < 2 seconds interactive
- Dashboard view (cached): < 500ms interactive
- Chart render: < 200ms per chart
- Lineage graph: < 1.5 seconds load

**Bundle Size Budgets**

- Main bundle: < 200 KB gzipped
- Dashboard view: < 150 KB additional
- Editor view: < 100 KB additional
- Recharts library: lazy loaded, < 80 KB

**Runtime Performance**

- 60 FPS during interactions
- Time to Interactive (TTI): < 3 seconds
- Total Blocking Time (TBT): < 300ms
- First Contentful Paint (FCP): < 1.5 seconds

**Network Efficiency**

- Single dashboard data request (no waterfall)
- Image assets: WebP format, lazy loaded
- Fonts: subset to used glyphs
- API responses: compressed (gzip/brotli)

**Quality Gates**

CI/CD checks block deployment if:
- Lighthouse performance score < 90
- Accessibility score < 95
- Bundle size exceeds budget
- Critical a11y violations present

### **11. View Type Specifications**

**Analytical View (Default)**

**Purpose**: Deep exploration and analysis

**Layout Characteristics**:
- Multi-column grid: 3-4 columns on desktop
- Widget density: Medium (balanced)
- Filter prominence: High (always visible)
- Chart size: Medium to Large
- Interaction density: High (drill-downs, comparisons)

**Default Widgets**:
- KPI tiles: top row, 4 across
- Time series charts: prominent, half to full width
- Comparison charts: side by side
- Detail tables: full width, scrollable

**Default Settings**:
- Time range: Last 90 days
- Refresh: Manual only
- Filters: Date, primary dimension

**Best For**:
- Ad-hoc investigation
- Trend analysis
- Cohort comparison
- Deep dives

---

**Operational View**

**Purpose**: Real-time monitoring and alerting

**Layout Characteristics**:
- Status-first hierarchy: alerts and KPIs above fold
- Widget density: High (more widgets, less whitespace)
- Alert prominence: High (banner area reserved)
- Chart size: Small to Medium
- Interaction density: Low (read-only focus)

**Default Widgets**:
- Alert banner: top, full width
- Status KPIs: large tiles, color-coded with thresholds
- Real-time trends: small sparklines
- Current state indicators: minimal chrome

**Default Settings**:
- Time range: Today / Last hour
- Refresh: Auto 30-60 seconds
- Filters: Minimal (service, region)

**Best For**:
- NOC dashboards
- Incident response
- System monitoring
- Live operations

---

**Strategic View**

**Purpose**: Executive summaries and presentations

**Layout Characteristics**:
- Narrative flow: top to bottom reading pattern
- Widget density: Low (generous whitespace)
- Text prominence: High (context and explanation)
- Chart size: Large, high-level only
- Interaction density: Minimal (view-only)

**Default Widgets**:
- Hero KPIs: very large, top center
- Key metrics summary: 2-3 tiles
- Narrative blocks: context paragraphs
- High-level trends: clean, simple charts
- No tables (except executive summary)

**Default Settings**:
- Time range: YTD / Fiscal period
- Refresh: Daily
- Filters: None or period only

**Best For**:
- Board presentations
- Executive reviews
- Strategy meetings
- Stakeholder updates

### **12. Acceptance Criteria (MVP)**

**Functional Requirements**

Routes and Navigation:
- [ ] All seven routes accessible and render correctly
- [ ] Navigation between routes maintains context
- [ ] Breadcrumbs show current location
- [ ] Back/forward browser buttons work correctly

Dashboard Gallery:
- [ ] Displays all user-accessible dashboards as cards
- [ ] Search filters dashboards by title/owner/tag
- [ ] Filter dropdown works for tags and owner
- [ ] New dashboard button opens creation flow
- [ ] Empty state shows when no dashboards exist

Dashboard View:
- [ ] All three view types (Analytical/Operational/Strategic) render correctly
- [ ] View type toggle changes layout and density
- [ ] Filters apply to all widgets and update URL
- [ ] Charts render with Recharts using backend data
- [ ] Tooltips show on chart hover with formatted values
- [ ] Tables sort by column header click
- [ ] Freshness timestamp visible per card
- [ ] Freshness color coding works (green/yellow/red)

Dashboard Editor:
- [ ] Builder tab shows visual widget layout
- [ ] Properties panel updates when widget selected
- [ ] Color/type/size changes reflect immediately
- [ ] YAML tab shows validated YAML text
- [ ] YAML validation highlights errors inline
- [ ] Preview tab renders full dashboard with live data
- [ ] Dirty state banner shows when changes unsaved
- [ ] Save button validates and persists to backend
- [ ] Confirmation dialog prevents losing unsaved work

Lineage View:
- [ ] Graph displays dashboard → charts → queries → tables
- [ ] Nodes color-coded by type
- [ ] Click node shows metadata panel
- [ ] Expand/collapse works for node hierarchy
- [ ] Search filters graph nodes
- [ ] "Open in Builder" navigates correctly

Datasets Explorer:
- [ ] Tree shows BigQuery projects/datasets/tables
- [ ] Click table loads schema in middle panel
- [ ] Preview shows sample rows (max 100)
- [ ] Partition and clustering info displayed
- [ ] Search filters tree by table name

Settings:
- [ ] Theme change applies immediately
- [ ] Date/number format changes reflect in dashboards
- [ ] Sign out clears session and redirects to login

**Performance Requirements**

- [ ] Dashboard view (cached): p95 < 500ms load
- [ ] Dashboard view (cold): p95 < 2s load
- [ ] Individual chart: p95 < 200ms render
- [ ] Editor: p95 < 3s Time to Interactive
- [ ] Main bundle: < 200 KB gzipped
- [ ] Lighthouse performance score: > 90

**Accessibility Requirements**

- [ ] All interactive elements reachable via keyboard
- [ ] Focus indicators visible (2px ring)
- [ ] Screen reader announces page changes
- [ ] Charts have text alternatives
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Zoom to 200% maintains usability
- [ ] No keyboard traps
- [ ] Lighthouse accessibility score: > 95

**Responsive Requirements**

- [ ] Mobile (< 640px): single column layout, readable
- [ ] Tablet (640-1024px): 2-3 columns, functional
- [ ] Desktop (> 1024px): full layout with rails
- [ ] Grid reflows without breaking at all breakpoints
- [ ] Touch targets minimum 44x44px on mobile

**Visual Requirements**

- [ ] Consistent spacing using design tokens
- [ ] ShadCN components used throughout
- [ ] Recharts charts render cleanly
- [ ] Loading skeletons show during data fetch
- [ ] Empty states provide clear next actions
- [ ] Error messages actionable with trace IDs

**Demonstration Requirements**

- [ ] Create dashboard from chat: successful end-to-end
- [ ] Edit chart color in Builder: persists after save
- [ ] YAML edit reflects in Preview: two-way binding works
- [ ] Lineage exploration: can trace data flow
- [ ] Responsive test: mobile, tablet, desktop all functional

### **13. Implementation Phasing**

**MVP (Weeks 1-8)**

Core page structure and routing:
- Application shell with three-panel layout
- Seven routes implemented
- Navigation between pages functional

Dashboard rendering:
- YAML-to-UI mapping engine
- Support for 4 chart types: line, bar, area, table
- KPI tiles with deltas
- Grid layout with responsive breakpoints

Editor functionality:
- Builder tab with visual editing
- YAML tab with syntax highlighting
- Preview tab with live data
- Save workflow with validation

Essential components:
- ShadCN base components integrated
- Recharts wrapped in ShadCN chart container
- Loading states and error boundaries
- Toast notifications

Acceptance:
- Two reference dashboards created via chat
- Visual edits persist after save
- All three view types render correctly
- Responsive on mobile, tablet, desktop

**Phase 1 (Weeks 9-12)**

Enhanced caching and freshness:
- Pub/Sub driven "New data available" banner
- Version hints in URLs
- Automatic freshness checks

Improved data handling:
- Table virtualization for long lists
- Chart annotation library (ReferenceLine/Area)
- Saved filter presets

Role-based features:
- Viewer vs Editor UI variations
- Read-only mode for shared dashboards

Performance optimizations:
- Bundle splitting improvements
- Memorystore cache reduces latency to <300ms

**Phase 2/3 (Months 4-6)**

Advanced visualizations:
- Custom widget types beyond Recharts
- Heatmaps, Sankey diagrams, network graphs

Dashboard templating:
- Variables/parameters editable in UI
- Date ranges and filters as parameters
- Template gallery

External context:
- Slack/Linear context panel
- LLM can reference external discussions
- Narrative composition tools

### **13.1 Implementation Status & Task Trace (2025-10-31)**

| Experience Area | Status | Task Reference | Notes |
|-----------------|--------|----------------|-------|
| App Shell & Navigation | ✅ Complete | docs/task.md (Frontend Phase 2.3) | Three-panel layout, responsive rails, and route scaffolding shipped in Phase 2. |
| Dashboard View (Analytical/Operational/Strategic) | 🚧 In Progress | docs/task.md (Frontend Phases 3.2 & 4.3) | Chart components live; widget layout, freshness badges, and operational auto-refresh still pending. |
| Dashboard Editor (Builder/YAML/Preview) | 📝 Planned | docs/task.md (Frontend Phase 5.1-5.6) | UI wireframes defined; implementation queued after dashboard view stabilizes. |
| LLM Assistant UX | 📝 Planned | docs/task.md (Frontend Phase 6.1-6.4) | Chat shell exists, but streaming flows + “Explain this” context not yet wired. |
| Schema Browser (Datasets Explorer) | 📝 Planned | docs/task.md (Frontend Phase 8.1) | UX spec finalized (lazy tree, schema preview, pagination) awaiting hook + endpoint integration. |
| Accessibility & Responsive Hardening | 🚧 In Progress | docs/task.md (Frontend Phase 9) | Keyboard focus outlines and AA colour compliance slated alongside autosave work. |

**Outstanding follow-ups**
- Deliver Phase 3.2 operational UX (alert banner, auto-refresh, “Next refresh” timestamp) so Operational view meets monitoring goals.
- Build layout-aware ChartGrid/YAML mapping to unlock Builder + Preview parity.
- Ensure datasets explorer honours backend caching windows (datasets 1h, tables 15m) and keeps preview uncached.

### **13.2 Decision Log (Updated)**
- **Three-view layout (Analytical/Operational/Strategic)** retained after prototype testing—aligns UI density with distinct user intents.
- **Schema browser interaction model**: hierarchical tree + metadata/preview panels, chosen to keep cognitive load low while surfacing BigQuery context.
- **Freshness signalling**: chart-level badges with colour semantics (green <1h, yellow 1–4h, red >4h, grey unknown) confirmed as MVP baseline.

### **13.3 Schema Browser UX Snapshot**
- Left navigation lists datasets with lazy expand; tables load on demand with virtualized scrolling.
- Metadata pane shows columns, types, partitioning, clustering plus quick copy-to-clipboard for column names.
- Preview tab paginates 50 rows (configurable ≤1000) and exposes “Load more” without caching raw data to honour freshness guarantees.

Collaboration:
- Multi-editor presence indicators
- Optimistic locking or operational transforms
- Comment threads on charts

Publishing and sharing:
- Public share links
- Embedded dashboards (iframe)
- Downloadable reports (PDF/PPTX)

### **14. Design System Reference**

**Typography**

```
Headings:
- h1: 32px semibold
- h2: 24px semibold
- h3: 20px semibold
- h4: 16px semibold

Body:
- Default: 16px regular
- Small: 14px regular
- Tiny: 12px regular

Numeric:
- KPI value: 28-32px semibold
- Chart label: 12px regular
- Table cell: 14px regular
```

**Spacing Scale**

```
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
```

**Color Palette**

```
Primary: Blue
- 50: #EFF6FF
- 500: #3B82F6 (main)
- 700: #1D4ED8 (dark)

Secondary: Gray
- 50: #F9FAFB
- 500: #6B7280 (text)
- 900: #111827 (heading)

Success: Green (#10B981)
Warning: Yellow (#F59E0B)
Error: Red (#EF4444)
```

**Grid System**

```
12-column responsive grid
Gutters: 16px mobile, 24px desktop
Max width: 1440px
Breakpoints:
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px
```

**Component Tokens**

```
Border radius:
- Small: 4px (buttons, inputs)
- Medium: 8px (cards, modals)
- Large: 12px (sheets, drawers)

Shadows:
- sm: 0 1px 2px rgba(0,0,0,0.05)
- md: 0 4px 6px rgba(0,0,0,0.07)
- lg: 0 10px 15px rgba(0,0,0,0.1)

Focus ring:
- Width: 2px
- Offset: 2px
- Color: Primary-500
```

### **15. Visual Encoding Guidelines**

**Chart Selection**

Use position and length as primary encoding channels:

**Line/Area Chart**: Time series trends
- X axis: temporal (date, datetime)
- Y axis: quantitative (revenue, count)
- Series: categorical (region, product)

**Bar Chart**: Discrete comparisons
- X axis: categorical (product, region)
- Y axis: quantitative (revenue, count)
- Horizontal bars for long category labels

**Table**: Precise values, multiple dimensions
- Use when exact numbers matter
- Support sorting and filtering
- Limit rows to prevent overwhelming

**KPI Tile**: Single metric monitoring
- Large value for quick scanning
- Delta shows trend direction
- Sparkline for context

**Avoid**:
- Pie charts (angles hard to compare)
- 3D charts (distort perception)
- Dual Y-axes (confusing scale)

**Visual Hierarchy**

Position matters:
- Top-left: most important
- Top row: KPIs and alerts
- Center: primary content
- Bottom: supporting details

Size indicates importance:
- Larger widgets = higher priority
- Consistent sizing within type
- Don't make everything large

Color for emphasis:
- Semantic: green (positive), red (negative)
- Categorical: distinct hues
- Quantitative: sequential scale
- Avoid rainbow (hard to interpret)

**Reference Lines and Areas**

Use Recharts ReferenceLine and ReferenceArea:
- Target thresholds: horizontal line
- Acceptable range: shaded area
- Notable events: vertical line
- SLA boundaries: dual reference lines

**Legend Placement**

- Bottom: preferred for horizontal space
- Right: when many series (>5)
- Top: rarely, only if chart very tall
- None: if series obvious from context

---

## **16. Open Questions**

**Design Decisions**

- Viewport support: How far down to support mobile? MVP assumes 375px minimum width.
- Dark mode default: Should dark mode be default or light? Needs design decision.
- Chart library: Fully committed to Recharts or keep option to evaluate D3.js?
- Animation: Should charts animate on load or prefer static for performance?

**UX Patterns**

- Collaboration: Real-time editing or async save-merge workflow?
- Navigation: Persistent left rail or collapsible for more content space?
- Filters: Always visible inline or collapsible panel?
- Mobile: Bottom tab bar or hamburger menu for navigation?

**Technical Constraints**

- Browser support: Latest 2 versions only, or support IE11/older browsers?
- Accessibility: Target WCAG 2.1 AA or AAA compliance?
- Performance: Hard block on budgets or soft warnings?

**Future Considerations**

- Print layout: Need print-friendly CSS for dashboard reports?
- Offline: Should dashboards cache for offline viewing?
- Embeds: Will dashboards be embedded in other applications?
- White-label: Need for customizable branding/themes?

---

## **17. Assumptions**

**User Behavior**

- Users primarily access on desktop during business hours
- Comfortable with modern web applications
- Understand basic analytics concepts (KPIs, trends, filters)
- Willing to learn YAML for advanced customization

**Technical Environment**

- Modern browsers: Chrome, Firefox, Safari, Edge (latest 2 versions)
- JavaScript enabled
- Adequate bandwidth for 200-300 KB payloads
- No corporate proxy blocking WebSocket (for future real-time)

**Content Constraints**

- Dashboards typically have 5-15 widgets
- Charts display 10-500 data points
- Tables show <1000 rows
- YAML files stay under 5000 lines

**Design System**

- ShadCN provides 90% of needed components
- Recharts covers standard visualization needs
- Tailwind sufficient for layout and spacing
- No custom illustration or iconography needed

---
