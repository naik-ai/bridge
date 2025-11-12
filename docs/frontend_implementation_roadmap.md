# Frontend Implementation Roadmap - MVP Completion

**Date**: 2025-11-12
**Current Status**: 55% Complete → Target: 100% by Week 3
**Estimated Effort**: 15 working days (3 weeks)

---

## Executive Summary

The design-system-architect agent has completed a comprehensive audit revealing:

### ✅ **Strengths**
- Solid architectural foundations (3-panel layout, state management, API client)
- Complete chart component library (5 types with Recharts)
- Dashboard viewing experience (85% complete)
- Clean TypeScript codebase with proper typing

### 🚨 **Critical Gaps**
1. **No Design Token System** - All styling uses raw Tailwind classes (FIXED)
2. **27 Duplicate Components** - `/components/` vs `/src/components/` inconsistency
3. **Editor 20% Complete** - BuilderMode, PropertyInspector, PreviewTab, SaveWorkflow missing
4. **No Accessibility Tooling** - Missing eslint-plugin-jsx-a11y, axe-core, Storybook
5. **Mock Data Everywhere** - API client exists but not integrated

### 📊 **MVP Progress**
- **Functional Criteria**: 5/12 complete (42%)
- **Component Library**: 48/75 components complete (64%)
- **Routes**: 2/7 critical routes implemented (29%)
- **Overall**: 55% → Need 45% more to ship MVP

---

## Completed Work (This Session)

### ✅ Design Token System Implementation

**Created**:
1. `/apps/web/src/lib/tokens.ts` (312 LOC)
   - Complete monotone color palette (black/white/grey for UI)
   - Semantic colors for data/status only (success, warning, error)
   - Typography tokens (Inter font, modular scale)
   - Spacing tokens (4px base rhythm)
   - Motion tokens (durations + easing curves)
   - Elevation, z-index, opacity tokens
   - TypeScript type safety with `as const`

2. Updated `/apps/web/tailwind.config.ts`
   - Imported tokens and integrated into Tailwind theme
   - Exposed token-based utility classes
   - Maintained ShadCN compatibility layer
   - Added font size, weight, transition utilities

**Impact**:
- Establishes single source of truth for all design decisions
- Enables systematic migration from hardcoded values
- Enforces monotone theme compliance
- Provides TypeScript autocomplete for design properties

---

## 3-Week Implementation Plan

### Week 1: Infrastructure & Editor (5 days)

**Critical Path**: Component consolidation → Editor components → Integration

#### Day 1-2: Component Consolidation & Infrastructure (16 hours)

**Task 1.1: Identify and Remove Duplicates** (4 hours)
```bash
# Duplicate files to remove:
/apps/web/components/ui/*.tsx (10 files)
/apps/web/components/layout/*.tsx (5 files)
/apps/web/components/charts/bar-chart.tsx
/apps/web/components/charts/line-chart.tsx
/apps/web/components/charts/kpi-card.tsx
/apps/web/components/charts/chart-card.tsx
/apps/web/components/dashboard/dashboard-editor.tsx
/apps/web/components/dashboard/dashboard-view.tsx

# Keep: All files in /apps/web/src/components/*
```

**Task 1.2: Update Imports** (2 hours)
```bash
# Find all imports from old location
grep -r "from '@/components/" apps/web/src/
grep -r "from '../components/" apps/web/src/

# Replace with new location (automated)
find apps/web/src -type f -name "*.tsx" -o -name "*.ts" | \
  xargs sed -i '' "s|from '@/components/|from '@/src/components/|g"
```

**Task 1.3: Install Dev Tools** (4 hours)
```bash
cd apps/web

# Storybook + addons
pnpm add -D @storybook/nextjs@latest \
  @storybook/addon-a11y \
  @storybook/addon-essentials \
  @storybook/react \
  storybook

# Accessibility linting
pnpm add -D eslint-plugin-jsx-a11y \
  @axe-core/react

# Visual regression
pnpm add -D lost-pixel

# Testing utilities
pnpm add -D @testing-library/react \
  @testing-library/jest-dom \
  @testing-library/user-event
```

**Task 1.4: Configure Storybook** (4 hours)
- Create `.storybook/main.ts` with Next.js 15 support
- Create `.storybook/preview.tsx` with monotone theme decorator
- Add first 5 stories (Button, Card, Input, Badge, Skeleton)
- Verify Storybook runs: `pnpm storybook`

**Task 1.5: Type Check & Build** (2 hours)
```bash
# Verify no broken imports
pnpm typecheck

# Test build
pnpm build

# Fix any compilation errors
```

#### Day 3-4: Editor Components (16 hours)

**Component 1: BuilderMode** (8 hours)
- File: `/apps/web/src/components/editor/BuilderMode.tsx`
- Features:
  - Wraps DashboardGrid with `isEditable={true}` mode
  - Click-to-select chart interaction
  - Blue outline on selected chart (2px solid ring)
  - Opens PropertyInspector on selection
  - Keyboard navigation (Tab, Enter, Escape)
- Props: `dashboardYaml`, `onYamlUpdate`, `viewType`, `readOnly`
- States: default, chart-selected, chart-hover, error
- Storybook: 5 stories (Default, WithCharts, ChartSelected, ErrorState, ReadOnly)

**Component 2: PropertyInspector** (8 hours)
- File: `/apps/web/src/components/editor/PropertyInspector.tsx`
- Features:
  - Right sidebar (35% width on desktop, modal on tablet)
  - Three tabs: Appearance, Data, Layout
  - Color picker (4 semantic colors: neutral, success, warning, error)
  - Size selector (Radio group: S, M, L, XL)
  - Type dropdown (Select: line, bar, area, kpi, table)
  - Title input with 50-char limit
  - Real-time YAML updates (debounced 500ms)
- Props: `chartConfig`, `onUpdate`, `onClose`, `validationErrors`
- Storybook: 4 stories (KPIChart, LineChart, ValidationErrors, ReadOnly)

#### Day 5: Preview Tab & Save Workflow (8 hours)

**Component 3: PreviewTab** (4 hours)
- File: `/apps/web/src/components/editor/PreviewTab.tsx`
- Features:
  - Live YAML rendering using DashboardGrid (read-only)
  - Error boundary for parse errors
  - Refresh button to re-parse
  - View type toggle (Analytical/Operational/Strategic)
  - Empty state: "No charts defined. Add charts in Builder tab."
- Props: `yamlContent`, `viewType`, `onViewTypeChange`
- Storybook: 4 stories (ValidYAML, ParseError, EmptyState, Loading)

**Component 4: SaveWorkflow** (2 hours)
- File: `/apps/web/src/components/editor/SaveWorkflow.tsx`
- Features:
  - Confirmation dialog (ShadCN Dialog component)
  - Three actions: Save, Discard, Cancel
  - Async save handler with loading state
  - Error state with retry button
  - Keyboard shortcuts (Enter = Save, Escape = Cancel)
- Props: `isDirty`, `onSave`, `onDiscard`, `onCancel`, `isOpen`
- Storybook: 4 stories (Default, Open, Saving, Error)

**Component 5: Editor Route** (2 hours)
- File: `/apps/web/src/app/edit/[slug]/page.tsx`
- Features:
  - Tab navigation (Builder | YAML | Preview)
  - Load dashboard YAML from backend
  - Dirty state indicator in header
  - Wire BuilderMode ↔ PropertyInspector
  - Wire SaveWorkflow to API client
- Integration with Zustand store for state management

---

### Week 2: Auth, Accessibility & Polish (5 days)

#### Day 1-2: Google SSO Implementation (16 hours)

**Backend Coordination** (2 hours)
- Verify `/auth/google` and `/auth/callback` endpoints exist
- Confirm session cookie format and expiration
- Test `/auth/me` endpoint for user info

**Frontend OAuth Flow** (6 hours)
- File: `/apps/web/src/components/auth/GoogleSSOButton.tsx`
  - Redirect to backend OAuth URL
  - Include CSRF token
  - Handle redirect callback with code
- File: `/apps/web/src/middleware.ts`
  - Protected route logic (check session cookie)
  - Redirect to `/login` if unauthenticated
  - Allow public routes: `/login`, `/`, `/auth/*`
- File: `/apps/web/src/app/login/page.tsx`
  - Update to use GoogleSSOButton
  - Handle OAuth errors from query params

**Session Management** (4 hours)
- Update `/apps/web/src/contexts/auth-context.tsx`
  - Fetch user from `/auth/me` on mount
  - Auto-refresh session every 5 minutes
  - Handle 401 responses (logout + redirect)
- Add logout handler to Header component
  - Call `/auth/logout` endpoint
  - Clear TanStack Query cache
  - Redirect to `/login`

**E2E Testing** (4 hours)
- Playwright test: Login flow with mock OAuth
- Playwright test: Protected route redirect
- Playwright test: Logout flow

#### Day 3-4: Accessibility Audit & Fixes (16 hours)

**Configure Linting** (2 hours)
```bash
# .eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:jsx-a11y/recommended"
  ],
  "plugins": ["jsx-a11y"]
}

# Run and fix
pnpm lint --fix
```

**Color Contrast Audit** (4 hours)
- Use axe DevTools extension on all pages
- Fix any failures (4.5:1 text, 3:1 interactive)
- Update FreshnessIndicator colors if needed
- Verify semantic colors meet contrast requirements

**Keyboard Navigation** (6 hours)
- Audit all interactive elements for Tab order
- Add missing `tabIndex` attributes
- Implement keyboard shortcuts:
  - BuilderMode: Tab (navigate), Enter (select), Delete (remove), Escape (deselect)
  - PropertyInspector: Tab (navigate), Escape (close)
  - SaveWorkflow: Enter (save), Escape (cancel)
- Test with keyboard only (no mouse)

**Screen Reader Support** (4 hours)
- Add ARIA labels to all charts: `role="img"`, `aria-label="Revenue trend chart"`
- Add ARIA live regions for dynamic updates
- Test with NVDA/JAWS/VoiceOver
- Add skip-to-content links

#### Day 5: Storybook Stories (8 hours)

**New Components** (4 hours)
- BuilderMode: 5 stories
- PropertyInspector: 4 stories
- PreviewTab: 4 stories
- SaveWorkflow: 4 stories

**Existing Components** (4 hours)
- Chart components: 18 stories (6 types × 3 states)
- Dashboard components: 6 stories
- Layout components: 2 stories
- UI components: 8 stories (high-priority only)

**Total**: 42 stories with a11y addon checks enabled

---

### Week 3: Secondary Features & Final QA (5 days)

#### Day 1-2: Lineage Graph (16 hours)

**Install React Flow** (1 hour)
```bash
pnpm add reactflow
```

**Component Implementation** (10 hours)
- File: `/apps/web/src/components/lineage/LineageGraph.tsx`
  - Force-directed or hierarchical layout
  - Nodes: Dashboard, Charts, Queries, Tables
  - Edges: Relationships (colored by type)
  - Pan and zoom controls
  - Click node → show metadata panel
  - Monotone theme (grey nodes, semantic edge colors)
- File: `/apps/web/src/components/lineage/NodeMetadataPanel.tsx`
  - Right sidebar with node details
  - For tables: schema, row count, last updated
  - For queries: SQL preview, bytes scanned
  - "Explain this" button (future: opens chat with context)

**Route Integration** (3 hours)
- File: `/apps/web/src/app/lineage/[slug]/page.tsx`
  - Fetch lineage data from backend `/lineage/:slug`
  - Render LineageGraph with data
  - Handle empty state (no lineage)

**Testing** (2 hours)
- Storybook: 3 stories (WithData, EmptyState, Loading)
- Playwright: Lineage navigation test

#### Day 3: Dataset Browser Route (8 hours)

**Route Wrapper** (2 hours)
- File: `/apps/web/src/app/datasets/page.tsx`
  - Wrap existing DatasetBrowser component
  - Add route to navigation (Explorer sidebar)

**API Integration** (4 hours)
- Update DatasetBrowser to use real API client
- Replace mock data with TanStack Query hooks
- Wire up `/v1/schema/datasets` and `/v1/schema/tables/:id`
- Add pagination for large datasets

**Testing** (2 hours)
- Storybook: 2 stories (WithData, Loading)
- Manual QA: Tree navigation, preview panel

#### Day 4-5: Performance Optimization & Final QA (16 hours)

**Bundle Size Analysis** (4 hours)
```bash
# Install bundle analyzer
pnpm add -D @next/bundle-analyzer

# Configure in next.config.ts
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

# Analyze
ANALYZE=true pnpm build
```
- Identify large dependencies
- Code split heavy routes (lineage, editor)
- Remove unused ShadCN components
- Target: <200KB main bundle

**Lighthouse Audit** (4 hours)
- Run Lighthouse on all pages
- Fix performance issues (LCP, CLS, TBT)
- Fix accessibility issues (any remaining)
- Target: Performance ≥90, Accessibility ≥95

**E2E Test Suite** (6 hours)
- Scenario 1: Dashboard editing flow (BuilderMode → PropertyInspector → Save)
- Scenario 2: YAML validation error recovery
- Scenario 3: Unsaved changes warning
- Scenario 4: Keyboard navigation (Tab through entire flow)
- Run tests in CI (GitHub Actions)

**Final Manual QA** (2 hours)
- Test all routes in production build
- Verify auth flow end-to-end
- Check responsive behavior (desktop, tablet)
- Verify monotone theme compliance
- Test keyboard-only navigation

---

## MVP Acceptance Criteria Checklist

### Functional Criteria (Frontend PDR §11)

- [ ] User can authenticate via Google SSO and access dashboard list
- [ ] Dashboard list displays all available dashboards with title and owner
- [x] Clicking dashboard navigates to view showing all charts rendered
- [x] Each chart displays as-of timestamp and freshness indicator
- [ ] User can initiate new dashboard via chat (PHASE 1.5 - deferred)
- [ ] User can save dashboard and it persists across sessions
- [ ] **Edit mode allows color changes via UI properties panel** (NEW - Week 1)
- [ ] **UI changes reflect back into in-memory YAML model** (NEW - Week 1)
- [x] YAML editor allows direct text editing with validation
- [ ] **Save workflow shows dirty state indicator before save** (NEW - Week 1)
- [ ] **Lineage view displays graph of dashboard composition** (NEW - Week 3)
- [ ] **Dataset browser accessible from navigation** (NEW - Week 3)

**Progress**: 3/12 complete → Target: 10/12 (chat deferred to Phase 1.5)

### Performance Criteria

- [ ] Dashboard page loads and renders in <3s on cold cache
- [x] Cached dashboard renders in <500ms (achieved with React Query)
- [x] Individual chart renders in <200ms (Recharts optimized)
- [ ] Time to interactive <3s on standard broadband
- [ ] Main JavaScript bundle <200KB gzipped

**Progress**: 2/5 complete → Target: 5/5

### Usability Criteria

- [ ] Non-technical user can create simple dashboard via chat (Phase 1.5)
- [x] User understands data freshness from visual indicators
- [ ] **Edit workflow intuitive: no training required** (NEW - Week 1)
- [ ] **Error messages actionable with clear next steps** (Week 2)
- [ ] **Lineage view navigable without instructions** (Week 3)

**Progress**: 1/5 complete → Target: 4/5 (chat deferred)

### Demonstration Criteria

- [ ] Create two distinct dashboards from scratch using chat (Phase 1.5)
- [ ] **Demonstrate UI edit changing chart color** (NEW - Week 1)
- [ ] **Show YAML editor changes rendering in visual view** (Week 1)
- [ ] **Navigate lineage view and explain data flow** (Week 3)

**Progress**: 0/4 complete → Target: 3/4 (chat deferred)

---

## Updated Task.md Status

### Phase Completion Summary

```markdown
## Frontend Implementation Status (2025-11-12)

### Phase 1: Foundation & Setup ✅ COMPLETE
- [x] Monorepo + pnpm workspaces
- [x] Tailwind CSS + ShadCN baseline
- [x] Next.js 15 App Router
- [x] TypeScript strict mode

### Phase 2: OpenAPI Client & Auth 🟡 80% COMPLETE
- [x] Generated TypeScript client (@peter/api-client)
- [x] Auth context with session provider
- [ ] **Google SSO OAuth flow** (Week 2, Day 1-2)

### Phase 3.1: Chart Components ✅ COMPLETE
- [x] All 5 chart types implemented
- [x] ChartRenderer factory pattern
- [x] Monotone theme compliance
- [x] Loading skeletons

### Phase 3.2: Dashboard Widgets 🟡 70% COMPLETE
- [x] DashboardGrid (12-column layout)
- [x] FreshnessIndicator (color-coded badges)
- [ ] FilterPanel (deferred to Phase 1)
- [ ] Auto-refresh (deferred to Phase 1)

### Phase 3.3: Design System ✅ COMPLETE (NEW)
- [x] Created `/src/lib/tokens.ts` (312 LOC)
- [x] Updated `tailwind.config.ts` with token integration
- [x] Established monotone theme compliance
- [ ] **Component migration to tokens** (Ongoing - Week 2)

### Phase 4: Dashboard Pages 🟡 60% COMPLETE
- [x] Gallery page with search
- [x] Dashboard view page
- [ ] **Replace mock data with API client** (Week 1, Day 5)

### Phase 5: YAML Editor & Builder 🚨 30% COMPLETE (CRITICAL)
- [x] YAML tab with syntax highlighting
- [x] YAML validation
- [ ] **BuilderMode component** (Week 1, Day 3)
- [ ] **PropertyInspector component** (Week 1, Day 3-4)
- [ ] **PreviewTab component** (Week 1, Day 5)
- [ ] **SaveWorkflow component** (Week 1, Day 5)
- [ ] **Editor route** `/edit/[slug]` (Week 1, Day 5)

### Phase 7: Lineage Graph 📝 PLANNED (Week 3)
- [ ] LineageGraph component (React Flow)
- [ ] NodeMetadataPanel sidebar
- [ ] Route `/lineage/[slug]/page.tsx`

### Phase 8: Dataset Browser 🟡 50% COMPLETE
- [x] DatasetBrowser component
- [ ] **Route `/datasets/page.tsx`** (Week 3, Day 3)
- [ ] **API integration** (Week 3, Day 3)

### Phase 9: Testing & QA 🚨 NEW PHASE
- [ ] **Storybook + a11y addon** (Week 1, Day 1-2)
- [ ] **42 component stories** (Week 2, Day 5)
- [ ] **Visual regression testing** (Week 2, Day 5)
- [ ] **Playwright E2E tests** (Week 3, Day 4-5)
- [ ] **Accessibility audit** (Week 2, Day 3-4)
- [ ] **Performance optimization** (Week 3, Day 4)
```

---

## Risk Mitigation Strategies

### CRITICAL RISKS

**Risk 1: Component Migration Breaks UI**
- **Mitigation**: Visual regression testing with Lost Pixel
- **Fallback**: Keep `/components/` directory for 1 week rollback window
- **Validation**: Run full E2E suite after migration

**Risk 2: Auth Integration Delays Editor**
- **Mitigation**: Mock auth with env var `MOCK_AUTH=true` for local dev
- **Fallback**: Ship MVP with basic email/password, add SSO in Phase 1
- **Timeline**: Start auth Day 1 of Week 2 (don't block editor)

**Risk 3: Two-Way YAML Binding Complexity**
- **Mitigation**: Comprehensive unit tests for yaml-parser.ts
- **Fallback**: Simplify to one-way binding (YAML → UI) for MVP
- **Testing**: Add 20+ test cases for edge cases

### HIGH RISKS

**Risk 4: Storybook Incompatibility with Next.js 15**
- **Mitigation**: Use official `@storybook/nextjs@latest`
- **Fallback**: Playwright component testing instead
- **Validation**: Test setup Day 1 of Week 1

**Risk 5: Performance Budget Exceeded**
- **Mitigation**: Aggressive code splitting, tree-shaking
- **Fallback**: Defer lineage graph to Phase 1
- **Target**: <200KB bundle, monitor throughout development

---

## Success Metrics

### Week 1 Targets
- ✅ Token system implemented
- [ ] 27 duplicate components removed
- [ ] 4 editor components built
- [ ] `/edit/[slug]` route functional
- [ ] Storybook configured with 5 stories

### Week 2 Targets
- [ ] Google SSO working end-to-end
- [ ] All accessibility linting errors fixed
- [ ] WCAG AA compliance validated
- [ ] 42 Storybook stories complete

### Week 3 Targets
- [ ] Lineage graph rendering
- [ ] Dataset browser integrated
- [ ] Bundle size <200KB
- [ ] Lighthouse scores: Performance ≥90, A11y ≥95
- [ ] All E2E tests passing

### Final MVP Targets
- **Functional**: 10/12 criteria met (83%)
- **Performance**: 5/5 criteria met (100%)
- **Usability**: 4/5 criteria met (80%)
- **Overall Progress**: 55% → 100%

---

## Next Steps (Immediate)

1. **Commit token system work** (5 minutes)
2. **Begin component consolidation** (start with duplicate removal script)
3. **Install Storybook** (verify compatibility)
4. **Create BuilderMode component** (start with skeleton)
5. **Schedule auth backend coordination** (confirm endpoints ready)

**Estimated Time to MVP**: 15 working days with focused execution on critical path.

**Blockers**: None identified (all dependencies resolvable internally)

**Go/No-Go Decision Point**: End of Week 1 - if editor components aren't functional, escalate for resource support.
