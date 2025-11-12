# Frontend Implementation Tasks

**Project**: Bridge (Peter Dashboard Platform) 
**Last Updated**: 2025-11-12
**Status**: Dashboard editor complete, onboarding and additional features pending

---

## Completion Summary

- **Phase 1**: ✅ Complete (Foundation & Setup)
- **Phase 2**: ✅ Complete (OpenAPI Client & Auth)
- **Phase 3.1**: ✅ Complete (Chart Components)
- **Phase 3.2**: ⏳ In Progress (Dashboard Widgets)
- **Phase 4**: ⏳ Pending (Dashboard Pages & Data Fetching)
- **Phase 5**: ✅ Complete (YAML Editor & Dashboard Editing)
- **Phase 0**: ⏳ Pending (Team Onboarding Wizard)

---

## Phase 1: Foundation & Setup ✅ COMPLETE

**Duration**: Completed 2025-10-30
**PDR Reference**: Frontend PDR §1

### 1.1 Project Setup
- [x] Initialize Next.js 15 with App Router
- [x] Configure TypeScript (strict mode)
- [x] Setup Tailwind CSS
- [x] Add ShadCN/UI components library
- [x] Configure path aliases (@/components, @/lib, etc.)

### 1.2 Design System
- [x] Create design token system (src/lib/tokens.ts)
  - Monotone color palette (black/white/grey)
  - Typography scale (Inter font)
  - Spacing tokens (4px rhythm)
  - Motion, elevation, responsive tokens
- [x] Update Tailwind config to consume tokens
- [x] Implement strict monotone theme

### 1.3 Project Structure
- [x] Create directory structure:
  - src/app/ (routes)
  - src/components/ (UI components)
  - src/lib/ (utilities, stores, API)
  - src/hooks/ (custom hooks)
  - src/types/ (TypeScript definitions)

---

## Phase 2: OpenAPI Client & Auth ✅ COMPLETE

**Duration**: Completed 2025-10-30
**PDR Reference**: Frontend PDR §2

### 2.1 API Client Generation
- [x] Generate TypeScript client from OpenAPI spec
- [x] Configure TanStack Query
- [x] Setup query client with defaults

### 2.2 Authentication
- [x] Google SSO button component
- [x] Auth context provider
- [x] Protected route middleware
- [x] Session management

---

## Phase 3: Charts & Dashboard Widgets

### Phase 3.1: Chart Components ✅ COMPLETE

**Duration**: Completed 2025-10-30
**PDR Reference**: Frontend PDR §3.1

- [x] LineChart component (Recharts wrapper)
- [x] BarChart component
- [x] AreaChart component
- [x] KpiTile component (value + delta + sparkline)
- [x] TableChart component (sortable, paginated)
- [x] ChartContainer (shared wrapper with monotone theme)
- [x] ChartRenderer (factory for chart types)

### Phase 3.2: Dashboard Widget Components ⏳ IN PROGRESS

**Duration**: ~4 hours | **Priority**: HIGH
**PDR Reference**: Frontend PDR §3.2

#### 3.2.1 Widget Containers
- [ ] DashboardWidget component
  - Title, description, actions menu
  - Loading skeleton
  - Error boundary
  - Freshness indicator

- [ ] FreshnessIndicator component
  - Green (<1h), Yellow (1-4h), Red (>4h), Grey (unknown)
  - Tooltip with exact timestamp
  - "As of Oct 30, 10:15 AM" format

#### 3.2.2 Empty States
- [ ] EmptyState component
  - Icon, title, description, action button
  - Used for no data, errors, first-time states

#### 3.2.3 Filter Components
- [ ] DateRangePicker component (ShadCN Calendar)
- [ ] FilterBar component (horizontal pill buttons)
- [ ] SavedFilters component (dropdown of presets)

---

## Phase 4: Dashboard Pages & Data Fetching ⏳ PENDING

**Duration**: ~6 hours | **Priority**: HIGH
**PDR Reference**: Frontend PDR §4
**Dependencies**: Backend Phase 4 (Data Serving) complete

### 4.1 Dashboard View Page (3 hours)

**Route**: `/dash/[slug]`

- [ ] Create page component (src/app/dash/[slug]/page.tsx)
- [ ] Implement data fetching:
  - useDashboard(slug) - Get dashboard metadata
  - useDashboardData(slug) - Get all chart data
  - Auto-refresh every 5 minutes (configurable)
- [ ] Implement layout rendering:
  - 12-column responsive grid
  - Position widgets per YAML layout
  - View type switching (analytical/operational/strategic)
- [ ] Add global controls:
  - Refresh button
  - Time range filter (quick selects: Today, Last 7d, Last 30d, Custom)
  - View type toggle
- [ ] Loading states:
  - Skeleton for each widget
  - Progressive rendering (show widgets as data arrives)
- [ ] Error handling:
  - Widget-level errors (show in widget, don't crash page)
  - Page-level errors (fallback UI)

### 4.2 Dashboard Gallery Page (2 hours)

**Route**: `/dashboards`

- [ ] Create gallery component
- [ ] Implement data fetching:
  - useDashboards() - List all dashboards
  - Filter by view_type, owner, tags
- [ ] Card layout:
  - Dashboard title, description
  - Preview thumbnail (first 3 charts)
  - Last updated timestamp
  - Quick actions: View, Edit, Delete
- [ ] Search and filter:
  - Search by title/description
  - Filter by view type
  - Sort by: Recent, Name, Owner
- [ ] Empty state: "No dashboards yet, create your first one"

### 4.3 Data Fetching Hooks (1 hour)

**File**: src/hooks/use-dashboard-data.ts

- [ ] useDashboard(slug) - TanStack Query hook
  - Fetches dashboard metadata
  - Caches for 5 minutes
  - Returns: {dashboard, isLoading, error}

- [ ] useDashboardData(slug) - TanStack Query hook
  - Fetches all chart data
  - Parallel queries for each chart
  - Caches per query_id
  - Returns: {data: {query_id: {data, metadata}}, isLoading, errors}

- [ ] useChartData(slug, query_id) - Single chart data
  - For individual widget refresh
  - Returns: {data, metadata, isLoading, error, refetch}

- [ ] useDashboardRefresh(slug) - Invalidate all queries
  - Force refresh all chart data
  - Show loading state during refresh

---

## Phase 5: YAML Editor & Dashboard Editing ✅ COMPLETE

**Duration**: Completed 2025-11-12
**PDR Reference**: Frontend PDR §5

### 5.1 Editor State Management ✅
- [x] Zustand editor store (src/lib/store/editor.ts)
  - Editor state: yaml, originalYaml, isDirty, selectedChartId, etc.
  - Actions: setYaml, updateChart, selectChart, markAsSaved
  - Dirty tracking: JSON.stringify comparison
  - Browser unload warning

### 5.2 Editor Components ✅
- [x] BuilderMode (src/components/editor/BuilderMode.tsx)
  - Visual grid editor with 12-column overlay
  - Click-to-select interaction
  - Keyboard navigation (Tab, Enter, Escape)
  - 2px solid focus indicators

- [x] PropertyInspector (src/components/editor/PropertyInspector.tsx)
  - Right sidebar (Sheet) at 320px/400px
  - Three tabs: Appearance, Data, Layout
  - Color picker (4 semantic colors)
  - Size selector, chart type selector
  - Debounced updates (500ms for text inputs)

- [x] YAMLEditor (src/components/editor/YAMLEditor.tsx)
  - Textarea with js-yaml parsing
  - Real-time validation (debounced 500ms)
  - Error display (parse vs validation errors)
  - Mono font styling

- [x] PreviewTab (src/components/editor/PreviewTab.tsx)
  - Live preview with view type toggle
  - Refresh button
  - Grid layout matching final render

- [x] SaveWorkflow (src/components/editor/SaveWorkflow.tsx)
  - Save button with loading state
  - AlertDialog with Save/Discard/Cancel
  - Browser unload warning hook

### 5.3 Editor Route ✅
- [x] Create /edit/[slug] page (src/app/edit/[slug]/page.tsx)
  - Header: Back button, title, dirty indicator, Save button
  - Three tabs: Builder, YAML, Preview
  - Property Inspector integration
  - Load dashboard on mount
  - Reset state on unmount

### 5.4 API Integration ✅
- [x] Dashboard type definitions (src/types/dashboard.ts)
- [x] API client (src/lib/api/dashboards.ts)
  - getDashboard, saveDashboard, validateDashboard
  - listDashboards, deleteDashboard
- [x] Query hooks (src/hooks/use-dashboards.ts)
  - useDashboard, useSaveDashboard, useValidateDashboard
  - Cache invalidation, toast notifications

### 5.5 Utilities ✅
- [x] Debounce utility (src/lib/utils/debounce.ts)
- [x] UI components: Alert, Separator, Input, Textarea, Label, RadioGroup

---

## Phase 0: Team Onboarding Wizard ⏳ PENDING

**Duration**: ~12 hours | **Priority**: HIGH - Required before dashboard creation
**PDR Reference**: Frontend PDR §0
**Dependencies**: Backend Phase 0 complete

### 0.1 State Management (2 hours)

**File**: src/stores/onboardingStore.ts

- [ ] Create Zustand onboarding store
  - State: currentStep (1-13), completedSteps[], team, connection, datasets, tables, etc.
  - Actions: nextStep, previousStep, jumpToStep, completeStep
  - Setters: setTeam, setConnection, addDatasets, addTables
- [ ] Implement sessionStorage persistence
  - Save on every state change
  - Load on mount
  - Key: `bridge_onboarding_state_{team_slug}`
- [ ] Add validation helpers:
  - canProceed(currentStep): boolean
  - getStepProgress(step): {completed, progress}
  - getOverallProgress(): number (percentage)

### 0.2 API Integration Hooks (2 hours)

**File**: src/hooks/useOnboardingAPI.ts

- [ ] Create TanStack Query hooks:
  - useCreateTeam, useInviteMembers
  - useCreateConnection, useValidateConnection
  - useTriggerCatalogScan, useCatalogJob (polling)
  - useDatasets, useTables
- [ ] Implement job polling pattern:
  - useJobPolling(jobId, jobType)
  - Polls every 2 seconds while status is "running"
  - Updates store with progress
  - Stops when "completed" or "failed"
- [ ] Add error handling:
  - Network errors: Retry with exponential backoff
  - 401: Redirect to login
  - 422: Field-level validation errors
  - 500: Show error with trace ID

### 0.3 Shared Components (3 hours)

#### 0.3.1 OnboardingLayout
**File**: src/components/onboarding/OnboardingLayout.tsx

- [ ] Three-panel layout:
  - 240px sidebar (step list)
  - Flex center (active step content)
  - 320px help panel (context-sensitive tips)
- [ ] Header: Logo, "Bridge Onboarding", Help button, Exit button
- [ ] Footer: Back button, Progress indicator, Next button
- [ ] Sidebar: Vertical step list with checkmarks for completed steps
- [ ] Responsive: Collapse sidebar/help on <1024px

#### 0.3.2 StepHeader
**File**: src/components/onboarding/StepHeader.tsx

- [ ] Props: stepNumber, title, description
- [ ] Display: "Step N of 3" badge, h2 title, description paragraph
- [ ] Monotone styling

#### 0.3.3 FileUpload
**File**: src/components/onboarding/FileUpload.tsx

- [ ] Drag-and-drop zone (240px height)
- [ ] File validation: JSON only
- [ ] Shows file name and size after upload
- [ ] Remove button, loading spinner, error state

#### 0.3.4 JobProgressCard
**File**: src/components/onboarding/JobProgressCard.tsx

- [ ] Props: jobStatus, progress (0-100), message
- [ ] Progress bar with status icon
- [ ] Auto-updates via polling hook

### 0.4 Step Components (5 hours)

**Simplified 3-Step Flow** (per task_reorganization_plan.md):

#### Step 1: Team Creation (1.5 hours)
**File**: src/components/onboarding/Step1TeamCreation.tsx

- [ ] Team name input (auto-generates slug)
- [ ] Slug preview (editable)
- [ ] Admin user display (current user)
- [ ] Member invite fields (optional, email + role)
- [ ] Add/remove invite buttons
- [ ] Validation: Team name required, slug unique
- [ ] API call: useCreateTeam, useInviteMembers
- [ ] On success: Save team to store, mark step complete, next step

#### Step 2: Connection Setup (1.5 hours)
**File**: src/components/onboarding/Step2ConnectionSetup.tsx

- [ ] Connection name input
- [ ] Warehouse type dropdown (BigQuery only for MVP)
- [ ] FileUpload component for service account JSON
- [ ] "Validate Connection" button
- [ ] Validation progress indicator
- [ ] Display validation result:
  - Success: Green checkmark, permissions summary
  - Failed: Red X, error message, retry button
- [ ] API calls: useCreateConnection, useValidateConnection
- [ ] On success: Save connection to store, mark step complete, next step

#### Step 3: Catalog Scan (2 hours)
**File**: src/components/onboarding/Step3CatalogScan.tsx

- [ ] "Start Catalog Scan" button
- [ ] JobProgressCard for scan progress
- [ ] Real-time updates via useJobPolling
- [ ] Display scan results:
  - Datasets found: N
  - Tables found: M
  - Scan duration: Xs
- [ ] Preview table: List of datasets with table counts
- [ ] "Continue to Dashboard Creation" button
- [ ] API calls: useTriggerCatalogScan, useCatalogJob
- [ ] On success: Save datasets/tables to store, mark onboarding complete, redirect to /dashboards

### 0.5 Onboarding Route (1 hour)

**Route**: `/onboarding`

- [ ] Create onboarding page (src/app/onboarding/page.tsx)
- [ ] Load onboarding store on mount
- [ ] Render OnboardingLayout with active step
- [ ] Handle navigation between steps
- [ ] Save state to sessionStorage
- [ ] On completion: Clear session, redirect to /dashboards

---

## Phase 6: LLM Chat Assistant ⏳ PENDING

**Duration**: ~8 hours | **Priority**: MEDIUM
**PDR Reference**: Frontend PDR §6
**Dependencies**: Backend Phase 3.11 (Chat API), Phase 3.5 (Dashboard Generation)

### 6.1 Chat State Management (1 hour)

**File**: src/stores/chatStore.ts

- [ ] Create Zustand chat store
  - State: sessions[], activeSessionId, messages[], isStreaming
  - Actions: createSession, sendMessage, addMessage, setActiveSession
- [ ] Message types:
  - user, assistant, tool_call, tool_result, error
- [ ] Streaming state management

### 6.2 Chat UI Components (4 hours)

#### 6.2.1 ChatPanel
**File**: src/components/chat/ChatPanel.tsx

- [ ] Collapsible right panel (320px)
- [ ] Session list dropdown
- [ ] Message list (scrollable, auto-scroll to bottom)
- [ ] Message input (textarea with submit button)
- [ ] "New Session" button
- [ ] Collapse/expand toggle

#### 6.2.2 ChatMessage
**File**: src/components/chat/ChatMessage.tsx

- [ ] User message: Right-aligned, grey background
- [ ] Assistant message: Left-aligned, white background
- [ ] Markdown rendering (code blocks, lists)
- [ ] Tool call display (collapsible JSON)
- [ ] Streaming indicator (typing animation)

#### 6.2.3 ChatInput
**File**: src/components/chat/ChatInput.tsx

- [ ] Textarea with auto-resize
- [ ] Submit button (Enter to send, Shift+Enter for newline)
- [ ] Character count (optional)
- [ ] Disabled while streaming

### 6.3 Chat API Integration (2 hours)

**File**: src/hooks/useChatAPI.ts

- [ ] useChatSessions() - List sessions
- [ ] useCreateSession() - Create new session
- [ ] useChatStream(sessionId) - SSE streaming hook
  - Handles event: token, event: tool_call, event: done
  - Appends tokens to message buffer
  - Updates store with tool calls
  - Handles errors
- [ ] useSessionHistory(sessionId) - Load message history

### 6.4 Dashboard Generation Integration (1 hour)

- [ ] "Generate Dashboard with AI" button in gallery
- [ ] Opens chat panel with pre-filled prompt
- [ ] Streams dashboard generation progress
- [ ] On completion: Navigate to /edit/[slug]
- [ ] Error handling: Show error, allow retry

---

## Phase 7: Lineage Visualization ⏳ PENDING

**Duration**: ~4 hours | **Priority**: LOW
**PDR Reference**: Frontend PDR §7
**Dependencies**: Backend Phase Y (Lineage API)

### 7.1 Lineage Graph Component

**File**: src/components/lineage/LineageGraph.tsx

- [ ] Use React Flow library
- [ ] Node types: Dashboard, Chart, Query, Table, Column
- [ ] Edge types: uses, derives_from
- [ ] Interactive: Click node → show metadata panel
- [ ] Layout: Hierarchical (top-to-bottom)
- [ ] Zoom and pan controls

### 7.2 Lineage Route

**Route**: `/lineage/[slug]`

- [ ] Load lineage data via API
- [ ] Render LineageGraph
- [ ] Metadata panel (right sidebar)
- [ ] Export to PNG button

---

## Phase 8: Additional Pages & Features ⏳ PENDING

### 8.1 Settings Page (2 hours)

**Route**: `/settings`

- [ ] User profile section
- [ ] Workspace preferences
- [ ] Theme toggle (light/dark)
- [ ] Data format settings (date, number, timezone)

### 8.2 Dataset Browser (3 hours)

**Route**: `/datasets`

- [ ] List all datasets from active connection
- [ ] Tree view: Connection → Datasets → Tables → Columns
- [ ] Search and filter
- [ ] Schema preview
- [ ] "Use in Dashboard" button (opens chat)

### 8.3 Help & Documentation (1 hour)

**Route**: `/help`

- [ ] Getting started guide
- [ ] YAML schema reference
- [ ] Keyboard shortcuts
- [ ] FAQ

---

## Phase 9: State Management & Error Handling ⏳ PENDING

### 9.1 Global Error Boundary (1 hour)

- [ ] App-level error boundary
- [ ] Route-level error boundaries
- [ ] Component-level error boundaries
- [ ] Error logging to backend

### 9.2 Toast Notifications (30 minutes)

- [ ] Already using Sonner (installed)
- [ ] Standardize toast patterns:
  - Success: Green checkmark
  - Error: Red X with trace ID
  - Info: Blue info icon
  - Warning: Yellow warning icon

### 9.3 Loading States (1 hour)

- [ ] Skeleton loaders for all data components
- [ ] Progress indicators for async operations
- [ ] Optimistic updates where appropriate

---

## Phase 10: Testing ⏳ PENDING

### 10.1 Component Tests (4 hours)

- [ ] Chart components
- [ ] Editor components
- [ ] Onboarding components
- [ ] React Testing Library
- [ ] Jest configuration

### 10.2 E2E Tests (4 hours)

- [ ] Playwright configuration
- [ ] Auth flow test
- [ ] Dashboard view test
- [ ] Editor workflow test
- [ ] Onboarding flow test

### 10.3 Visual Regression (2 hours)

- [ ] Chromatic or Percy setup
- [ ] Snapshot tests for key pages
- [ ] Monotone theme compliance checks

---

## Phase 11: Deployment & Documentation ⏳ PENDING

### 11.1 Vercel Deployment (1 hour)

- [ ] Configure Vercel project
- [ ] Environment variables
- [ ] Preview deployments for PRs
- [ ] Production deployment

### 11.2 Performance Optimization (2 hours)

- [ ] Code splitting by route
- [ ] Image optimization
- [ ] Bundle size analysis
- [ ] Lighthouse audit (target: >90)

### 11.3 Documentation (2 hours)

- [ ] Component documentation (Storybook)
- [ ] README with setup instructions
- [ ] Architecture diagram
- [ ] Contributing guide

---

## Phase 12: MVP Validation & Demo ⏳ PENDING

### 12.1 Demo Preparation (2 hours)

- [ ] Create sample dashboards
- [ ] Populate with real data
- [ ] Record demo video
- [ ] Prepare presentation deck

### 12.2 User Testing (4 hours)

- [ ] Recruit 5-10 initial users
- [ ] Conduct usability tests
- [ ] Collect feedback
- [ ] Prioritize improvements

---

## Dependencies & Prerequisites

### External Libraries:
- Next.js 15 (App Router)
- React 18
- TypeScript 5
- Tailwind CSS 3
- ShadCN/UI (Radix UI primitives)
- TanStack Query 5
- Zustand 4
- Recharts 2
- js-yaml 4
- date-fns 3
- lucide-react (icons)

### Environment Variables:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## Design System Guidelines

### Monotone Theme (Strict):
- **UI Chrome**: Black/white/grey ONLY
- **Data Colors**: Semantic colors ONLY (neutral/success/warning/error)
- **Focus**: 2px solid ring (black in light mode, white in dark)
- **Typography**: Inter font, 400-600 weights
- **Spacing**: 4px rhythm (x1, x2, x3, x4, x6, x8)

### Accessibility:
- WCAG AA compliance (4.5:1 contrast)
- Keyboard navigation (Tab, Enter, Escape)
- ARIA labels and roles
- Screen reader support
- Focus indicators visible

### Performance Budgets:
- Main bundle: <200 KB gzipped
- Dashboard view: <150 KB additional
- Load time: <500ms cached, <2s cold
- Chart render: <200ms per chart

---

**Last Updated**: 2025-11-12
**Next Priority**: Phase 0 (Onboarding Wizard) → Phase 4 (Dashboard Pages) → Phase 6 (Chat Assistant)
