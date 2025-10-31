# Peter Platform - UX Wireframes & User Journey

**Version**: 1.0
**Last Updated**: 2025-10-31
**Status**: Complete Specification for Phase 0 Implementation

---

## Table of Contents

1. [Design System Summary](#1-design-system-summary)
2. [User Journey Overview](#2-user-journey-overview)
3. [Authentication Flow](#3-authentication-flow)
4. [Team Onboarding Flow (13 Steps)](#4-team-onboarding-flow)
5. [Dashboard Interface](#5-dashboard-interface)
6. [Component Library](#6-component-library)
7. [Responsive Patterns](#7-responsive-patterns)
8. [Accessibility Guidelines](#8-accessibility-guidelines)

---

## 1. Design System Summary

### 1.1 Monotone Color Palette

**CRITICAL**: This project uses a strict **black/white/grey monotone theme**.

```
Background Tones:
├─ bg-primary:    #FFFFFF (light) / #0A0A0A (dark)
├─ bg-secondary:  #F9F9F9 (light) / #171717 (dark)
└─ bg-tertiary:   #F3F3F3 (light) / #262626 (dark)

Text Tones:
├─ text-primary:   #0A0A0A (light) / #FAFAFA (dark)
├─ text-secondary: #525252 (both modes)
└─ text-tertiary:  #737373 (both modes)

Border/Divider:
└─ border: #E5E5E5 (light) / #404040 (dark)

Accent (minimal use):
├─ Selection/Focus: #0A0A0A (light) / #FAFAFA (dark)
└─ Hover: subtle opacity shift (90% → 100%)

Semantic Colors (data/status ONLY):
├─ Success: #10B981 (status indicators only)
├─ Warning: #F59E0B (alerts only)
├─ Error:   #EF4444 (errors only)
└─ Neutral: grey for non-sentiment data
```

**Color Usage Rules**:
- **NO branded colors** in UI chrome (no blues, greens, reds for buttons/navigation)
- Use semantic colors ONLY for data/status indicators
- Charts use **greyscale gradients** as default
- Focus rings: 2px solid black (light mode) or white (dark mode)

### 1.2 Typography Scale

**Font Family**: Inter (system fallback: -apple-system, BlinkMacSystemFont, sans-serif)

| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| h1 | 32px | 600 | 1.2 | Page titles |
| h2 | 24px | 600 | 1.3 | Section headers |
| h3 | 20px | 600 | 1.4 | Subsection headers |
| h4 | 16px | 600 | 1.5 | Card headers |
| body | 16px | 400 | 1.5 | Default text |
| small | 14px | 400 | 1.5 | Supporting text |
| tiny | 12px | 400 | 1.4 | Metadata, labels |
| kpi-value | 28-32px | 600 | 1.0 | Numeric KPIs (tabular-nums) |

### 1.3 Spacing Scale

```
4px   - Tight spacing (icon padding)
8px   - Compact spacing (form field gaps)
16px  - Default spacing (card padding)
24px  - Medium spacing (section gaps)
32px  - Large spacing (major sections)
48px  - XL spacing (page divisions)
64px  - XXL spacing (hero sections)
```

### 1.4 Grid System

- **12-column responsive grid**
- Gutters: 16px (mobile), 24px (desktop)
- Max content width: 1440px
- Breakpoints:
  - Mobile: <640px
  - Tablet: 640-1024px
  - Desktop: >1024px

### 1.5 Border Radius

```
4px  - Small (inputs, small buttons)
8px  - Medium (cards, medium components)
12px - Large (modals, large containers)
```

---

## 2. User Journey Overview

### 2.1 Complete User Flow Map

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       PETER PLATFORM USER JOURNEY                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Phase 1: AUTHENTICATION                                                  │
│  ├─→ Landing Page                                                         │
│  ├─→ Google SSO Login                                                     │
│  ├─→ Email Allowlist Verification                                         │
│  └─→ Success → Onboarding OR Dashboard (returning user)                  │
│                                                                           │
│  Phase 2: TEAM ONBOARDING (13 Steps - Phase 0)                            │
│  ├─→ Steps 1-3: Team Setup                                                │
│  │   ├─ Step 1: Welcome & Team Name                                       │
│  │   ├─ Step 2: Team Members                                              │
│  │   └─ Step 3: Team Preferences                                          │
│  ├─→ Steps 4-6: Data Connection & Discovery                               │
│  │   ├─ Step 4: Connect BigQuery                                          │
│  │   ├─ Step 5: Dataset Discovery                                         │
│  │   └─ Step 6: Table Schema Preview                                      │
│  ├─→ Steps 7-8: LLM-Assisted Setup                                        │
│  │   ├─ Step 7: LLM Dashboard Generation                                  │
│  │   └─ Step 8: Business Goals Definition                                 │
│  └─→ Steps 9-12: Governance & Finalization                                │
│      ├─ Step 9: Cost Estimation & Verification                            │
│      ├─ Step 10: Workspace Preferences                                    │
│      ├─ Step 11: Onboarding Summary Report (HTML)                         │
│      └─ Step 12: Completion & Next Steps                                  │
│                                                                           │
│  Phase 3: DASHBOARD INTERFACE (Post-Onboarding)                           │
│  ├─→ Dashboard Gallery (3-panel layout)                                   │
│  ├─→ Dashboard Detail View (3 view types)                                 │
│  │   ├─ Analytical (exploration-focused)                                  │
│  │   ├─ Operational (status-focused)                                      │
│  │   └─ Strategic (narrative-focused)                                     │
│  ├─→ Dashboard Editor                                                     │
│  │   ├─ Builder Tab (drag-and-drop)                                       │
│  │   ├─ YAML Tab (code editor)                                            │
│  │   └─ Preview Tab (live rendering)                                      │
│  └─→ Lineage View (graph visualization)                                   │
│                                                                           │
│  Phase 4: ONGOING USAGE                                                   │
│  ├─→ Create New Dashboards                                                │
│  ├─→ Collaborate with Team                                                │
│  ├─→ Monitor Data Freshness                                               │
│  └─→ Manage Datasets & Permissions                                        │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key User Personas

| Persona | Primary Goal | Key Workflow | Pain Points |
|---------|-------------|--------------|-------------|
| **Data Analyst** | Create analytical dashboards | Onboarding → Catalog Review → Dashboard Creation → Iteration | Complex SQL, slow queries |
| **Team Admin** | Setup team workspace | Complete all onboarding steps → Configure governance → Invite team | Configuration overhead |
| **Business User** | View operational KPIs | Direct dashboard access → Monitor metrics → Export data | Data freshness uncertainty |
| **Executive** | Strategic insights | View strategic dashboards → Review trends → Share reports | Too much detail, want narrative |

---

## 3. Authentication Flow

### 3.1 Login Screen (Unauthenticated)

```text
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                                                                       │
│                         ┌─────────────┐                              │
│                         │             │                              │
│                         │    Peter    │                              │
│                         │     Logo    │                              │
│                         │             │                              │
│                         └─────────────┘                              │
│                                                                       │
│                   Dashboard Intelligence Platform                    │
│                                                                       │
│                                                                       │
│                                                                       │
│              ┌───────────────────────────────────────┐              │
│              │                                         │              │
│              │  ┌───────────────────────────────────┐ │              │
│              │  │                                     │ │              │
│              │  │  [G] Sign in with Google           │ │              │
│              │  │                                     │ │              │
│              │  └───────────────────────────────────┘ │              │
│              │                                         │              │
│              │    By signing in, you agree to our      │              │
│              │    Terms of Service and Privacy Policy. │              │
│              │                                         │              │
│              └───────────────────────────────────────┘              │
│                                                                       │
│                                                                       │
│                         Version 0.1.0 • MVP                           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

DIMENSIONS:
- Container: 400px width, centered vertically & horizontally
- Logo: 80px height
- Sign-in button: Full width, 48px height
- Minimum viewport height: 600px

COMPONENTS (ShadCN):
- Button: variant="default", size="lg"
- Logo: SVG, monotone (black light/white dark)
- Legal text: text-secondary, 12px, hover:underline

BUTTON STATES:
Default:  bg-primary, border-2 border-black, text-black
Hover:    bg-black, text-white
Focus:    2px solid focus ring offset 2px
Loading:  Disabled + spinner "Signing in..."
Disabled: opacity-40, cursor-not-allowed

ACCESSIBILITY:
- aria-label="Sign in with Google OAuth"
- Keyboard: Tab to button, Enter to activate
- Screen reader: "Sign in with Google button. Redirects to Google authentication."
- Focus visible: High contrast ring
```

### 3.2 OAuth Redirect (Loading State)

```text
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                                                                       │
│                         ┌─────────────┐                              │
│                         │    Peter    │                              │
│                         │     Logo    │                              │
│                         └─────────────┘                              │
│                                                                       │
│                                                                       │
│                       ┌─────────────────┐                            │
│                       │   ● ● ●         │                            │
│                       │   Loading...    │                            │
│                       └─────────────────┘                            │
│                                                                       │
│                Verifying your credentials...                          │
│                                                                       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

COMPONENTS:
- Spinner: 24px diameter, border-2, border-t-black, animate-spin
- Status text: text-secondary, 14px
- Background: bg-primary

TIMING:
- Typical: 1-3 seconds
- Timeout: 10 seconds → error state
- Auto-retry: 1 attempt after network error

ACCESSIBILITY:
- aria-live="polite" on status text
- aria-busy="true" on loading container
- Screen reader announces: "Loading, verifying your credentials"
```

### 3.3 Authorization Success (Redirect)

```text
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                         ┌─────────────┐                              │
│                         │    Peter    │                              │
│                         └─────────────┘                              │
│                                                                       │
│              ┌───────────────────────────────────────┐              │
│              │                                         │              │
│              │      ┌────┐                            │              │
│              │      │ ✓  │ Welcome back!              │              │
│              │      └────┘                            │              │
│              │                                         │              │
│              │  Redirecting to your workspace...       │              │
│              │                                         │              │
│              └───────────────────────────────────────┘              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

BEHAVIOR:
- Shows for 1 second
- Auto-redirects to:
  - /onboarding if new user (no team setup)
  - /dashboards if returning user

COMPONENTS:
- Success card: bg-secondary, border-2 border-success
- Icon: Checkmark, 32px, success color
- Text: text-primary, 16px
```

### 3.4 Authorization Error (Unauthorized Email)

```text
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                         ┌─────────────┐                              │
│                         │    Peter    │                              │
│                         └─────────────┘                              │
│                                                                       │
│              ┌───────────────────────────────────────┐              │
│              │                                         │              │
│              │      ┌────┐                            │              │
│              │      │ ⚠  │ Access Denied              │              │
│              │      └────┘                            │              │
│              │                                         │              │
│              │  Your email (user@example.com) is not   │              │
│              │  authorized to access Peter.            │              │
│              │                                         │              │
│              │  Contact your administrator to request  │              │
│              │  access.                                │              │
│              │                                         │              │
│              │  Error ID: err_auth_${timestamp}        │              │
│              │                                         │              │
│              │  ┌─────────────────────────────────┐   │              │
│              │  │   Return to Sign In              │   │              │
│              │  └─────────────────────────────────┘   │              │
│              │                                         │              │
│              └───────────────────────────────────────┘              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

COMPONENTS:
- Error card: bg-tertiary, border-2 border-error
- Icon: Warning triangle, 24px, error color
- Error ID: text-tertiary, 10px, monospace
- Button: ShadCN Button (variant="outline")

STATES:
- Button hover: bg-secondary
- Button focus: 2px ring

ACCESSIBILITY:
- role="alert" on error container
- aria-describedby points to error message
- Error ID copyable (click to copy)
```

---

## 4. Team Onboarding Flow

### 4.1 Onboarding Layout (All Steps 1-13)

```text
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ [Peter] Team Onboarding                                [Save & Exit ×]       │
├────────────┬──────────────────────────────────────────────────────────┬────────────────┤
│            │                                                           │                │
│  SIDEBAR   │                  CENTER CONTENT                          │  HELP PANEL    │
│  (240px)   │                  (flex, min 400px)                       │  (320px)       │
│            │                                                           │                │
│ Progress:  │  ┌────────────────────────────────────────────────────┐ │  Context       │
│ 25% (3/13) │  │  Step Title (h2, 24px/600)                         │ │  current step  │
│            │  │                                                     │ │                │
│ Steps:     │  │  Step description (16px/400)                        │ │  Tips:         │
│            │  │                                                     │ │  • Tip 1       │
│ ✓ Step 1   │  └────────────────────────────────────────────────────┘ │  • Warning     │
│ ✓ Step 2   │                                                           │  • Example     │
│ → Step 3   │  [Step-specific content area]                             │                │
│ • Step 4   │                                                           │  [Collapse]    │
│ • Step 5   │                                                           │                │
│ • Step 6   │                                                           │                │
│ • Step 7   │                                                           │                │
│ • Step 7   │                                                           │                │
│ • Step 8   │                                                           │                │
│ • Step 9  │                                                           │                │
│ • Step 10  │                                                           │                │
│ • Step 11  │                                                           │                │
│ • Step 12  │                                                           │                │
│            │                                                           │                │
└────────────┴──────────────────────────────────────────────────────────┴────────────────┘
│  [← Back]              Auto-saved 2 min ago • Step 3 of 13             [Next →]        │
└───────────────────────────────────────────────────────────────────────────────────────┘

LAYOUT SPECIFICATIONS:
- Total width: Responsive (min 1024px for full layout)
- Sidebar: Fixed 240px, scrollable if steps overflow
- Center: Flex-grow, min 400px, max 800px
- - Footer: Fixed 72px height, sticky

COMPONENTS:
- Progress bar: 8px height, bg-tertiary, filled: bg-black
- Step indicators:
  - ✓ Completed: text-primary, checkmark icon
  - → Current: text-primary, bold, arrow icon
  - • Pending: text-tertiary, circle icon
- Buttons: ShadCN Button (primary/outline)

NAVIGATION RULES:
- "Back" disabled on Step 1
- "Next" disabled if current step validation fails
- "Save & Exit" triggers confirmation dialog
- Auto-save every 2 minutes (debounced on user input)
- Session storage persists state

RESPONSIVE:
- Desktop (>1024px): Full 3-panel layout
- Tablet (640-1024px): Sidebar auto-collapses to overlay drawer
- Mobile (<640px): Single panel; panels access via bottom sheet

ACCESSIBILITY:
- Sidebar: role="navigation", aria-label="Onboarding progress"
- Main: role="main", aria-labelledby="step-title"
- Progress: aria-valuenow="3", aria-valuemin="1", aria-valuemax="13"
- Live region announces step changes: "Now on step 3 of 13: Team Preferences"
```

### 4.2 Step 1: Welcome & Team Name

```text
┌──────────────────────────────────────────────────────────────────┐
│  Step 1 of 13: Welcome to Peter                     [Skip Setup] │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Welcome, Sarah! Let's get your team set up.                      │
│                                                                   │
│  First, what should we call your workspace?                       │
│                                                                   │
│  Team Name *                                                      │
│  ┌────────────────────────────────────────────────────────┐      │
│  │ Revenue Analytics Team                                  │      │
│  └────────────────────────────────────────────────────────┘      │
│  This will be displayed in the app header and notifications.     │
│                                                                   │
│                                                                   │
│                               ┌──────────────┐                   │
│                               │  Continue     │                   │
│                               └──────────────┘                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

DIMENSIONS:
- Input: Full width, 48px height, 16px padding
- Container: Max 600px centered

COMPONENTS (ShadCN):
- Input: variant="default"
- Button: variant="default", size="default"
- Label: text-sm, text-secondary

VALIDATION:
- Required: Yes (asterisk shown)
- Min length: 3 characters
- Max length: 50 characters
- Pattern: Any printable characters
- Error: "Team name is required" (text-error, below input)

STATES:
Default: border-gray, bg-white
Focus: border-black, 2px ring
Error: border-error, error message below
Valid: subtle checkmark icon right-aligned
Disabled: opacity-40

ACCESSIBILITY:
- Label for="team-name"
- aria-required="true"
- aria-describedby="team-name-helper"
- Error announced with aria-live="polite"
```

### 4.3 Step 2: Team Members (Invite)

```text
┌──────────────────────────────────────────────────────────────────┐
│  Step 2 of 13: Invite Team Members                  [Skip Setup] │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Who else should have access to this workspace?                   │
│                                                                   │
│  Email addresses (one per line)                                   │
│  ┌────────────────────────────────────────────────────────┐      │
│  │ mike@company.com                                        │      │
│  │ alex@company.com                                        │      │
│  │ jordan@company.com                                      │      │
│  │                                                         │      │
│  │                                                         │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                   │
│  Role for all invitees:  [Editor ▼]                               │
│                                                                   │
│  ☐ Send invitation emails now                                    │
│                                                                   │
│                                                                   │
│                 ┌───────────┐  ┌──────────────┐                 │
│                 │  Skip      │  │  Continue     │                 │
│                 └───────────┘  └──────────────┘                 │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

COMPONENTS:
- Textarea: 5 rows, monospace font for emails
- Select: ShadCN dropdown
- Checkbox: ShadCN checkbox

ROLE OPTIONS:
- Viewer: Read-only access
- Editor: Create and edit dashboards
- Admin: Full workspace management

VALIDATION:
- Each line must be valid email format
- Duplicate detection (show warning icon, allow continue)
- Invalid emails: Red text color on that line

STATES:
Empty state: "Skip" and "Continue" both enabled
Has emails: Validate on blur
Checkbox unchecked: Invites saved but not sent

ACCESSIBILITY:
- Textarea aria-label="Team member email addresses"
- Role dropdown keyboard navigable
- Checkbox label clickable
```

### 4.4 Step 3: Team Preferences

```text
┌──────────────────────────────────────────────────────────────────┐
│  Step 3 of 13: Team Preferences                     [Skip Setup] │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Default Theme                                                    │
│  ● Light   ○ Dark   ○ System                                      │
│                                                                   │
│  Default Timezone                                                 │
│  [America/Los_Angeles (PST/PDT) ▼]                                │
│                                                                   │
│  Date Format                                                      │
│  ● MM/DD/YYYY   ○ DD/MM/YYYY   ○ YYYY-MM-DD                       │
│                                                                   │
│  Number Format                                                    │
│  ● 1,234.56   ○ 1.234,56   ○ 1 234.56                             │
│                                                                   │
│  Currency                                                         │
│  [USD ($) ▼]                                                      │
│                                                                   │
│                                                                   │
│                 ┌───────────┐  ┌──────────────┐                 │
│                 │  Back      │  │  Continue     │                 │
│                 └───────────┘  └──────────────┘                 │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

DEFAULTS:
- Theme: System (respects OS setting)
- Timezone: Auto-detected from browser
- Date: MM/DD/YYYY (US format)
- Number: 1,234.56 (US format)
- Currency: USD

COMPONENTS:
- Radio groups: ShadCN RadioGroup
- Select: ShadCN Select with search

BEHAVIOR:
- Changes apply immediately to preview
- Example text shows format: "Oct 31, 2025" or "2025-10-31"

ACCESSIBILITY:
- Radio groups have fieldset/legend
- Each radio has associated label
- Dropdowns keyboard navigable (arrow keys)
```

### 4.5 Step 4: Connect BigQuery

```text
┌──────────────────────────────────────────────────────────────────┐
│  Step 4 of 13: Connect Data Source                  [Skip Setup] │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Connect your data warehouse to start creating dashboards.        │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐       │
│  │  ┌──────────────────┐  ┌──────────────────┐          │       │
│  │  │   BigQuery        │  │  Snowflake        │          │       │
│  │  │   [Selected ✓]    │  │  [Coming Soon]    │          │       │
│  │  └──────────────────┘  └──────────────────┘          │       │
│  └───────────────────────────────────────────────────────┘       │
│                                                                   │
│  BigQuery Configuration                                           │
│                                                                   │
│  GCP Project ID *                                                 │
│  ┌────────────────────────────────────────────────────────┐      │
│  │ my-analytics-project                                    │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                   │
│  Service Account Key (JSON) *                                     │
│  ┌────────────────────────────────────────────────────────┐      │
│  │ {                                                       │      │
│  │   "type": "service_account",                            │      │
│  │   "project_id": "my-analytics-project",                 │      │
│  │   ...                                                   │      │
│  │ }                                                       │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                   │
│  Or: [Choose File] service-account.json                           │
│                                                                   │
│                                                                   │
│                 ┌───────────┐  ┌──────────────┐                 │
│                 │  Back      │  │  Test & Save  │                 │
│                 └───────────┘  └──────────────┘                 │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

VALIDATION:
- Project ID: Required, alphanumeric + hyphens
- JSON: Valid service account structure
- Test connection runs: SELECT 1 (dry_run=True)

LOADING STATE (during test):
┌────────────────────────────────────────────────────────────┐
│ ● Testing connection...                                     │
│ Running test query: SELECT 1 AS test                        │
└────────────────────────────────────────────────────────────┘

SUCCESS STATE:
┌────────────────────────────────────────────────────────────┐
│ ✓ Connection successful                                     │
│ Connected to: my-analytics-project                          │
│ Permissions verified: datasets.list, tables.list, jobs.create│
└────────────────────────────────────────────────────────────┘

ERROR STATE:
┌────────────────────────────────────────────────────────────┐
│ ✗ Connection failed                                         │
│ Error: Permission denied on project                         │
│ Error ID: err_bq_auth_123                                   │
│                                                             │
│ [Retry Connection]                                          │
└────────────────────────────────────────────────────────────┘

ACCESSIBILITY:
- File input hidden, triggered via label
- JSON textarea has monospace font
- Test results announced via aria-live
```

### 4.6 Step 5: Dataset Discovery

```text
┌──────────────────────────────────────────────────────────────────┐
│  Step 5 of 13: Discover Datasets                    [Skip Setup] │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  We found 23 datasets in your BigQuery project.                   │
│                                                                   │
│  Search datasets...                                               │
│  ┌────────────────────────────────────────────────────────┐      │
│  │ [🔍] revenue                                            │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐       │
│  │ ☑ analytics.revenue_daily_mv                           │       │
│  │   Last updated: 2 hours ago • 2.3M rows                │       │
│  ├───────────────────────────────────────────────────────┤       │
│  │ ☑ analytics.revenue_by_region                          │       │
│  │   Last updated: 1 day ago • 450K rows                  │       │
│  ├───────────────────────────────────────────────────────┤       │
│  │ ☐ analytics.customer_cohorts                           │       │
│  │   Last updated: 3 days ago • 1.1M rows                 │       │
│  ├───────────────────────────────────────────────────────┤       │
│  │ ☐ analytics.product_catalog                            │       │
│  │   Last updated: 1 week ago • 50K rows                  │       │
│  └───────────────────────────────────────────────────────┘       │
│                                                                   │
│  2 of 23 selected                                                 │
│                                                                   │
│                 ┌───────────┐  ┌──────────────┐                 │
│                 │  Back      │  │  Continue     │                 │
│                 └───────────┘  └──────────────┘                 │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

FEATURES:
- Real-time search filtering
- Click anywhere on row to toggle selection
- Freshness color coding:
  - Green: <4 hours
  - Yellow: 4-24 hours
  - Red: >24 hours

COMPONENTS:
- Search Input: ShadCN Input with search icon
- Checkbox list: ShadCN Checkbox in card
- Selection counter: text-secondary

INTERACTIONS:
- Search debounced 300ms
- Empty search result: "No datasets match 'revenue'"

ACCESSIBILITY:
- Each row button role with checkbox state
- Search aria-label="Search datasets"
- Selection count announced on change
```

---

## 5. Dashboard Interface

### 5.1 Main 3-Panel Layout

```text
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  Peter                                         sarah@company.com  [Settings ▼] [⚙]    │
├────────────┬─────────────────────────────────────────────────────────┬───────────────┤
│            │                                                         │               │
│  EXPLORER  │                 WORKSPACE                               │   ASSISTANT   │
│  (240px)   │                 (flex-grow)                             │   (320px)     │
│            │                                                         │               │
│ ┌────────┐ │ ┌─────────────────────────────────────────────────┐   │ ┌───────────┐ │
│ │Dashbrd │ │ │ Revenue Overview          ⊗  Builder  YAML  ⌄│   │ │  Chat     │ │
│ │Datasets│ │ ├─────────────────────────────────────────────────┤   │ │  (Stub)   │ │
│ │Recent  │ │ │                                                 │   │ │           │ │
│ │        │ │ │  [Dashboard content area]                       │   │ │  "Coming  │ │
│ │Search  │ │ │                                                 │   │ │   soon"   │ │
│ │───────│ │ │                                                 │   │ │           │ │
│ │• Rev   │ │ │                                                 │   │ │           │ │
│ │  Overv │ │ │                                                 │   │ │           │ │
│ │• Sales │ │ │                                                 │   │ │           │ │
│ │  Perf  │ │ │                                                 │   │ │           │ │
│ │• Cust  │ │ │                                                 │   │ │           │ │
│ │  Ret.  │ │ │                                                 │   │ │           │ │
│ │        │ │ │                                                 │   │ │           │ │
│ └────────┘ │ └─────────────────────────────────────────────────┘   │ └───────────┘ │
│            │                                                         │               │
└────────────┴─────────────────────────────────────────────────────────┴───────────────┘

PANEL BEHAVIORS:
- Explorer: Collapsible (◀ icon), min 200px, max 400px
- Workspace: Always visible, min 600px
- Assistant: Collapsible (▶ icon), min 280px, max 500px

RESPONSIVE:
- Desktop (>1024px): All panels visible
- Tablet (640-1024px): Explorer overlay drawer
- Mobile (<640px): Workspace only, panels via drawer

ACCESSIBILITY:
- role="navigation" on Explorer
- role="main" on Workspace
- role="complementary" on Assistant
- Resize handles have aria-labels
```

---

## 6. Component Library

### 6.1 Buttons

```text
PRIMARY BUTTON
┌─────────────────┐
│  Primary Action │  ← bg-black, text-white
└─────────────────┘

SECONDARY BUTTON
┌─────────────────┐
│ Secondary Action│  ← bg-transparent, border-2, text-black
└─────────────────┘

GHOST BUTTON
┌─────────────────┐
│  Ghost Action   │  ← bg-transparent, text-secondary, no border
└─────────────────┘

STATES:
- Hover: opacity 90% (primary) or bg-secondary (secondary/ghost)
- Focus: 2px ring offset 2px
- Active: scale 98%
- Disabled: opacity 40%, cursor-not-allowed
- Loading: Spinner replaces text

SIZES:
- sm: 32px height, 12px text
- md: 40px height, 14px text (default)
- lg: 48px height, 16px text
```

### 6.2 Form Inputs

```text
TEXT INPUT
┌───────────────────────────────────┐
│ Label                              │
│ ┌─────────────────────────────┐   │
│ │ Placeholder text...          │   │
│ └─────────────────────────────┘   │
│ Helper text here                   │
└───────────────────────────────────┘

STATES:
- Default: border-gray, bg-white
- Hover: border-gray-dark
- Focus: border-black, 2px ring
- Error: border-error, helper text red
- Success: border-success (optional)
- Disabled: opacity-50, bg-gray-100

SELECT DROPDOWN
┌───────────────────────────────────┐
│ Label                              │
│ ┌─────────────────────────────┐   │
│ │ Selected value            ▼ │   │
│ └─────────────────────────────┘   │
└───────────────────────────────────┘

Dropdown open:
┌─────────────────────────────┐
│ Option 1                     │
│ Option 2 ✓ (selected)        │
│ Option 3                     │
└─────────────────────────────┘

CHECKBOX
☑ Checked label
☐ Unchecked label

RADIO BUTTON
● Selected option
○ Unselected option
```

---

## 7. Responsive Patterns

### 7.1 Breakpoints

```
Mobile:     < 640px
Tablet:     640px - 1024px
Desktop:    > 1024px
Wide:       > 1440px
```

### 7.2 Layout Transformations

**Desktop (>1024px) - 12 columns:**
```
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│KPI│KPI│KPI│KPI│   │   │   │   │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
```

**Tablet (640-1024px) - 6 columns:**
```
┌───┬───┬───┬───┬───┬───┐
│KPI│KPI│KPI│KPI│   │   │
└───┴───┴───┴───┴───┴───┘
```

**Mobile (<640px) - 1 column:**
```
┌───────────────┐
│ KPI 1         │
├───────────────┤
│ KPI 2         │
├───────────────┤
│ Chart (scroll)│
└───────────────┘
```

---

## 8. Accessibility Guidelines

### 8.1 Keyboard Navigation

```
GLOBAL:
- Tab: Forward navigation
- Shift+Tab: Backward
- Enter/Space: Activate
- Escape: Close modal/drawer
- Arrow keys: Within components

DASHBOARD:
- Tab: Move between filters/charts
- Enter on chart: Detail view
```

### 8.2 ARIA Support

```
LANDMARKS:
<header role="banner">
<nav role="navigation" aria-label="Explorer">
<main role="main">
<aside role="complementary" aria-label="Assistant">

LIVE REGIONS:
<div aria-live="polite"> (status updates)
<div aria-live="assertive"> (errors)

LABELS:
- Charts: role="img" aria-label="Revenue trend..."
- Buttons: aria-label="Save dashboard"
- Inputs: aria-labelledby, aria-describedby
```

### 8.3 Color Contrast

```
WCAG AA COMPLIANCE (4.5:1):
- text-primary on bg-primary: 21:1 ✓
- text-secondary on bg-primary: 7.5:1 ✓
- text-tertiary on bg-primary: 4.6:1 ✓

FOCUS INDICATORS:
- 2px solid ring
- Offset 2px from element
- High contrast in all themes
```

---

### 4.7 Step 6: Table Schema Preview

**After dataset discovery completes, user can explore schemas before proceeding.**

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│  Step 6 of 13: Review Table Schemas                         [← Back] [Next →] │
│  Explore your discovered tables and sample their data                          │
├────────────────────────────────────────────────────────────────────────────────┤
│  Dataset Filter                                                                │
│  ┌─────────────────────────────────────────────────┐                          │
│  │ analytics_prod ▼                                 │                          │
│  └─────────────────────────────────────────────────┘                          │
│                                                                                │
│  TABLES (12 discovered)                             [Search: ___________]     │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ 📊 revenue_daily                                      [View Schema →]   │  │
│  │    Partitioned by: date | Size: 2.3 GB | Rows: 1.2M                    │  │
│  ├────────────────────────────────────────────────────────────────────────┤  │
│  │ 📊 user_events                                        [View Schema →]   │  │
│  │    Partitioned by: timestamp | Size: 15.8 GB | Rows: 45M              │  │
│  ├────────────────────────────────────────────────────────────────────────┤  │
│  │ 📊 product_catalog                                    [View Schema →]   │  │
│  │    Not partitioned | Size: 450 MB | Rows: 125K                         │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  SELECTED TABLE: revenue_daily                         [× Close Preview]      │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ SCHEMA (8 columns)                                                      │  │
│  │ ┌────────────────┬─────────────┬──────────┬──────────────────────────┐ │  │
│  │ │ Column         │ Type        │ Mode     │ Description              │ │  │
│  │ ├────────────────┼─────────────┼──────────┼──────────────────────────┤ │  │
│  │ │ date           │ DATE        │ REQUIRED │ Partition column         │ │  │
│  │ │ region         │ STRING      │ NULLABLE │ Geographic region        │ │  │
│  │ │ product_id     │ STRING      │ NULLABLE │ Product identifier       │ │  │
│  │ │ revenue        │ FLOAT64     │ NULLABLE │ Daily revenue USD        │ │  │
│  │ └────────────────┴─────────────┴──────────┴──────────────────────────┘ │  │
│  │                                                                         │  │
│  │ SAMPLE ROWS (5 of 1.2M)                              [Run Sample Query] │  │
│  │ ┌────────────┬────────┬────────────┬──────────┐                       │  │
│  │ │ date       │ region │ product_id │ revenue  │                       │  │
│  │ ├────────────┼────────┼────────────┼──────────┤                       │  │
│  │ │ 2025-10-30 │ US     │ PRD-001    │ 12450.50 │                       │  │
│  │ │ 2025-10-30 │ EU     │ PRD-001    │ 8320.75  │                       │  │
│  │ │ 2025-10-30 │ APAC   │ PRD-002    │ 4560.00  │                       │  │
│  │ └────────────┴────────┴────────────┴──────────┘                       │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

COMPONENTS (ShadCN):
- Select: Dataset filter dropdown
- Card: Table list items with hover states
- Table: Schema and sample data display
- Button: "View Schema", "Run Sample Query" (secondary)

INTERACTIONS:
- Click table → Expands preview panel below
- Click "View Schema" → Toggle schema detail
- Click "Run Sample Query" → Fetches 5 sample rows (BQ dry run first)
- Search input filters table list in real-time

PERFORMANCE:
- Sample query: Uses LIMIT 5, dry run to check bytes scanned
- Lazy loading: Schema details fetched on demand
- Virtualization: Table list if >50 tables

VALIDATION:
- At least 1 table must be discovered to proceed
- No user action required (informational step)
```

---

### 4.8 Step 7: LLM Dashboard Generation

**Use natural language to generate custom dashboard with Claude.**

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│  Step 8 of 13: Generate Dashboard with AI                [← Back] [Skip →]    │
│  Describe your dashboard needs in plain language                              │
├────────────────────────────────────────────────────────────────────────────────┤
│  What would you like to analyze?                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ I need a dashboard showing revenue trends by region over the last      │  │
│  │ 90 days, with a KPI tile for total revenue and a breakdown by product  │  │
│  │ category. Include YoY comparison.                                       │  │
│  │                                                                          │  │
│  │                                                                          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│  [💬 Generate Dashboard]                                                       │
│                                                                                │
│  ──────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│  GENERATION PROGRESS                                                           │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ ✓ Understanding request...                                   (2s)      │  │
│  │ ✓ Identifying relevant tables...                             (3s)      │  │
│  │   → Found: revenue_daily, product_catalog                              │  │
│  │ ⏳ Generating SQL queries...                                  (5s)      │  │
│  │   → Query 1: Total revenue KPI                                         │  │
│  │   → Query 2: Revenue trend by region                                   │  │
│  │   → Query 3: Product category breakdown                                │  │
│  │ ⏳ Validating queries...                                      (4s)      │  │
│  │   [████████████░░░░░░] 66% (2/3 verified)                              │  │
│  │ ⏳ Building dashboard layout...                               (2s)      │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ──────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│  GENERATED DASHBOARD PREVIEW                                [× Discard]       │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  revenue-trends-dashboard                                               │  │
│  │  ┌────────────┬────────────────────────────────────────────┐           │  │
│  │  │ Total Rev  │  Revenue Trend (Last 90 Days)              │           │  │
│  │  │ $2.4M      │  [Line Chart Thumbnail]                    │           │  │
│  │  │ +12% YoY   │                                             │           │  │
│  │  └────────────┴────────────────────────────────────────────┘           │  │
│  │  ┌──────────────────────────────────────────────────────────┐          │  │
│  │  │  Product Category Breakdown                              │          │  │
│  │  │  [Bar Chart Thumbnail]                                   │          │  │
│  │  └──────────────────────────────────────────────────────────┘          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  Queries: 3 | Estimated bytes: 45 MB | View type: Analytical                 │
│                                                                                │
│  [✏️ Edit YAML]  [👁️ Full Preview]  [✅ Accept & Save]                        │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

COMPONENTS (ShadCN):
- Textarea: Natural language input (min-height: 120px)
- Button: "Generate Dashboard" (primary, with loading state)
- Progress: Step indicators with checkmarks/spinners
- Card: Dashboard preview thumbnail
- Dialog: Full preview modal (when clicking "Full Preview")

INTERACTIONS:
- Click "Generate Dashboard" → Starts LLM generation
- Real-time progress updates via SSE (Server-Sent Events)
- Query validation failures show inline errors with retry option
- Click "Edit YAML" → Opens YAML in editor modal
- Click "Accept & Save" → Creates dashboard, marks step complete
- Click "Discard" → Clears generation, allows new prompt

LLM INTEGRATION:
- POST /api/v1/llm/generate-dashboard with prompt + team context
- Backend streams progress events: "understanding", "identifying", "generating", "validating", "building"
- Validation loop: Execute queries with 10 MB byte cap, return metadata
- If validation fails: Agent iterates up to 3 times before failing
- Circuit breaker: Max 5 concurrent LLM calls per team

COST TRACKING:
- Input tokens + output tokens logged in QueryLog
- User sees estimated cost in preview (based on bytes scanned)
- Generation failure surfaces error with trace_id

VALIDATION:
- Optional step (can skip)
- Prompt minimum: 20 characters
- Generated YAML must pass schema validation
- All SQL queries must execute successfully (or user acknowledges failures)
```

---

### 4.9 Step 8: Business Goals Mapping

**Map business objectives to datasets using LLM-powered suggestions.**

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│  Step 9 of 13: Map Business Goals                       [← Back] [Next →]     │
│  Connect your business objectives to relevant data sources                     │
├────────────────────────────────────────────────────────────────────────────────┤
│  Enter your team's business goals (one per line)                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Increase monthly recurring revenue by 15% in Q1                        │  │
│  │ Reduce customer churn rate below 5%                                    │  │
│  │ Improve product adoption in EMEA region                                │  │
│  │                                                                          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│  Or [📄 Import from file] (.txt, .csv)                                        │
│                                                                                │
│  [🔗 Map Goals to Datasets]                                                    │
│                                                                                │
│  ──────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│  MAPPED GOALS (3)                                                              │
│                                                                                │
│  Goal 1: Increase monthly recurring revenue by 15% in Q1                      │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ SUGGESTED DATASETS (Confidence: High)                                   │  │
│  │ • revenue_daily (95% match)                                             │  │
│  │   → Reason: Contains MRR, date, region columns                          │  │
│  │ • subscription_events (82% match)                                       │  │
│  │   → Reason: Tracks subscription changes over time                       │  │
│  │                                                                          │  │
│  │ KEY METRICS TO TRACK:                                                   │  │
│  │ • SUM(revenue) GROUP BY MONTH                                           │  │
│  │ • Growth rate vs. previous quarter                                      │  │
│  │                                                                          │  │
│  │ [✓ Accept Mapping]  [🔄 Retry]  [✏️ Edit Manually]                      │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  Goal 2: Reduce customer churn rate below 5%                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ SUGGESTED DATASETS (Confidence: Medium)                                 │  │
│  │ • user_events (68% match)                                               │  │
│  │   → Reason: Contains user activity, last_seen timestamps                │  │
│  │ • subscription_events (71% match)                                       │  │
│  │   → Reason: Tracks cancellation events                                  │  │
│  │                                                                          │  │
│  │ ⚠️  Suggestion: Consider creating a churn_cohorts derived table         │  │
│  │                                                                          │  │
│  │ [✓ Accept Mapping]  [🔄 Retry]  [✏️ Edit Manually]                      │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  Goal 3: Improve product adoption in EMEA region                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ ⏳ Mapping in progress...                                                │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

COMPONENTS (ShadCN):
- Textarea: Multi-line goal input
- Button: "Map Goals to Datasets", "Import from file"
- Card: Goal mapping results with confidence badges
- Badge: Confidence indicator (High/Medium/Low)
- Alert: Warnings for low confidence or missing data

INTERACTIONS:
- Click "Map Goals" → Sends goals to LLM service
- Real-time mapping appears as each goal completes
- Click "Accept Mapping" → Saves goal-dataset relationships to DB
- Click "Retry" → Re-runs LLM mapping for that goal
- Click "Edit Manually" → Opens picker to select datasets directly

LLM INTEGRATION:
- POST /api/v1/llm/map-business-goals with goals array + dataset metadata
- Agent uses catalog schema, column names, descriptions to find matches
- Returns confidence score (0-100) + reasoning snippet
- Parallel processing: Map all goals concurrently (respects 5-call limit)
- Fallback: If LLM unavailable, offer manual dataset selection

PERSISTENCE:
- Accepted mappings stored in business_goals table:
  - id, team_id, goal_text, suggested_datasets (JSONB), confidence, accepted_at
- Used later for governance policy suggestions and reporting

VALIDATION:
- Optional step (can skip)
- Minimum 1 goal required if mapping
- Accepted mappings must have >50% confidence or manual override
```

---

### 4.11 Step 9: Cost Estimation & Verification

**Review estimated BigQuery costs and run verification dry runs.**

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│  Step 10 of 13: Cost Estimation & Verification          [← Back] [Next →]     │
│  Review query costs and verify BigQuery access                                │
├────────────────────────────────────────────────────────────────────────────────┤
│  ESTIMATED MONTHLY COSTS                                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │  │
│  │  │ Query Scans      │  │ Storage          │  │ Total Estimate   │     │  │
│  │  │ $45.00           │  │ $12.00           │  │ $57.00           │     │  │
│  │  │ ~900 GB/month    │  │ 600 GB active    │  │ Per month        │     │  │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘     │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  COST BREAKDOWN BY QUERY                                [Show Details ▼]      │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Query                        │ Est. Bytes │ Est. Cost │ Daily Runs      │  │
│  ├──────────────────────────────┼────────────┼───────────┼─────────────────┤  │
│  │ revenue_daily_summary        │ 120 MB     │ $0.60     │ 1x              │  │
│  │ user_engagement_metrics      │ 450 MB     │ $2.25     │ 4x              │  │
│  │ product_performance_trend    │ 85 MB      │ $0.43     │ 2x              │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  VERIFICATION CHECKS                                                           │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ ✓ Service account has BigQuery permissions            [Verified]       │  │
│  │ ✓ All datasets are accessible                         [Verified]       │  │
│  │ ✓ Partition filters applied correctly                 [Verified]       │  │
│  │ ⏳ Running dry runs for cost validation...             [In Progress]    │  │
│  │   [████████████████░░░░] 80% (4/5 queries)                             │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  DRY RUN RESULTS                                        [Download Logs ↓]     │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ ✓ revenue_daily_summary                                                 │  │
│  │   Actual bytes: 118 MB | Job ID: job_abc123                            │  │
│  │                                                                          │  │
│  │ ✓ user_engagement_metrics                                               │  │
│  │   Actual bytes: 445 MB | Job ID: job_def456                            │  │
│  │                                                                          │  │
│  │ ⚠️  product_performance_trend                                            │  │
│  │   Actual bytes: 520 MB (6x higher than estimate!)                      │  │
│  │   Recommendation: Add partition filter on date column                   │  │
│  │   [View Query →]                                                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  [🔄 Re-run Verification]                              [Accept & Continue →]  │
└────────────────────────────────────────────────────────────────────────────────┘

COMPONENTS (ShadCN):
- Card: KPI tiles for cost summary
- Table: Query-level cost breakdown
- Progress: Verification progress bar
- Alert: Warnings for high-cost queries
- Button: "Re-run Verification", "Download Logs", "Accept & Continue"

INTERACTIONS:
- Auto-runs verification on page load
- Click "Show Details" → Expands cost breakdown table
- Click "View Query" → Opens SQL in modal with highlighted issues
- Click "Re-run Verification" → Triggers new dry runs
- Warnings require acknowledgment before continuing
- Click "Download Logs" → Exports dry run results as JSON

BACKEND LOGIC:
- Cost estimation: Sum of (bytes_scanned * $5/TB) across all queries
- Dry runs: BigQuery jobs with dry_run=true (no actual execution)
- Actual bytes compared to estimate, flag if >2x difference
- Verification checks:
  1. Service account IAM roles (bigquery.dataViewer, bigquery.jobUser)
  2. Dataset accessibility (INFORMATION_SCHEMA query)
  3. Partition filter validation (check WHERE clause for partition columns)
  4. Dry run execution (capture job metadata)

COST TRACKING:
- Verification results stored in cost_estimates table:
  - query_hash, estimated_bytes, actual_bytes_dry_run, timestamp
- Displayed in settings/cost dashboard later
- Alerts if monthly budget threshold exceeded

VALIDATION:
- At least 1 query must be verified
- All queries must complete dry run (or user acknowledges failures)
- No blocking errors (permissions, dataset not found, etc.)
```

---

### 4.12 Step 10: Workspace Preferences

**Configure default dashboard view types, refresh behavior, and layout preferences.**

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│  Step 11 of 13: Workspace Preferences                   [← Back] [Next →]     │
│  Customize your dashboard experience                                          │
├────────────────────────────────────────────────────────────────────────────────┤
│  DEFAULT VIEW TYPE                                                             │
│  Choose the primary view for new dashboards                                   │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  ○ Analytical   • Operational   ○ Strategic                             │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  Description: High-refresh monitoring with alert banners, KPI rail, and       │
│  compact widgets. Auto-refresh enabled by default (30s intervals).            │
│                                                                                │
│  ──────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│  AUTO-REFRESH BEHAVIOR                                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Enable auto-refresh for Operational dashboards?                         │  │
│  │ [☑ Yes, auto-refresh enabled]                                           │  │
│  │                                                                          │  │
│  │ Default refresh interval:                                               │  │
│  │ ○ 15s   • 30s   ○ 60s   ○ 5min                                         │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ──────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│  PANEL LAYOUT                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Default panel visibility:                                               │  │
│  │ [☑ Explorer (left rail)]                                                │  │
│  │ [☐ Assistant (right panel)] — Coming soon in Phase 1                   │  │
│  │                                                                          │  │
│  │ Explorer default width: [240px ▼]                                       │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ──────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│  LOCALE & FORMATS                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Timezone:          [America/Los_Angeles ▼]                              │  │
│  │ Date format:       [MM/DD/YYYY ▼]                                       │  │
│  │ Number format:     [1,234.56 (US) ▼]                                    │  │
│  │ Currency:          [USD ($) ▼]                                          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ──────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│  THEME                                                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Appearance:  ○ Light   ○ Dark   • System (follows OS preference)       │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

COMPONENTS (ShadCN):
- RadioGroup: View type selection, refresh interval, theme
- Checkbox: Auto-refresh toggle, panel visibility
- Select: Timezone, date/number/currency formats, explorer width
- Label: Field descriptions with helper text

INTERACTIONS:
- View type selection updates description text
- Auto-refresh checkbox enables/disables interval radio group
- Format selections show live preview in helper text
- All changes auto-save (debounced 2s)
- Toast notification on save: "Preferences saved"

PERSISTENCE:
- Stored in user_preferences table:
  - user_id, team_id, default_view_type, auto_refresh_enabled, refresh_interval_sec,
    explorer_visible, assistant_visible, timezone, date_format, number_format, currency, theme
- Applied globally across all dashboards for this team
- Individual dashboards can override (stored in dashboard metadata)

DEFAULTS:
- View type: Analytical
- Auto-refresh: Disabled (except Operational view)
- Refresh interval: 30s
- Explorer visible: Yes (240px)
- Assistant visible: No (Phase 1)
- Timezone: UTC (or browser detected)
- Formats: Based on browser locale
- Theme: System preference

VALIDATION:
- All fields optional (fallback to defaults)
- Refresh interval: 15s min, 5min max
- Explorer width: 200px min, 400px max
```

---

### 4.13 Step 11: Onboarding Summary Report

**Review completed onboarding steps and generate HTML summary.**

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│  Step 12 of 13: Onboarding Summary                      [← Back] [Next →]     │
│  Review your setup and generate a summary report                              │
├────────────────────────────────────────────────────────────────────────────────┤
│  ONBOARDING CHECKLIST                                   [Refresh Status ↻]    │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ ✓ Team created: Revenue Analytics Team                                 │  │
│  │ ✓ Team members invited: 3 members                                      │  │
│  │ ✓ BigQuery connection validated                                        │  │
│  │ ✓ Catalog scan completed: 12 tables discovered                         │  │
│  │ ✓ Table schemas reviewed                                               │  │
│  │ ○ Starter templates imported: Skipped                                  │  │
│  │ ✓ Dashboard generated: revenue-trends-dashboard                        │  │
│  │ ✓ Business goals mapped: 3 goals                                       │  │
│  │ ✓ Cost estimation verified: $57/month estimate                         │  │
│  │ ✓ Workspace preferences configured                                     │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  TEAM SUMMARY                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Name:         Revenue Analytics Team                                    │  │
│  │ Owner:        sarah@company.com                                         │  │
│  │ Members:      4 total (2 editors, 1 viewer, 1 admin)                   │  │
│  │ Datasets:     analytics_prod, user_behavior                             │  │
│  │ Tables:       12 discovered                                             │  │
│  │ Dashboards:   1 created                                                 │  │
│  │ Est. Cost:    $57/month                                                 │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  NEXT STEPS                                                                    │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ 1. Invite remaining team members from Settings                          │  │
│  │ 2. Explore your first dashboard: revenue-trends-dashboard               │  │
│  │ 3. Customize dashboard layout in the Builder                            │  │
│  │ 4. Set up data freshness alerts (Phase 1)                               │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  GENERATE SUMMARY REPORT                                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Create an HTML summary of your onboarding setup.                        │  │
│  │                                                                          │  │
│  │ [📄 Generate Summary]                                                    │  │
│  │                                                                          │  │
│  │ ⏳ Generating report...                                                  │  │
│  │ [████████████████████] 100%                                             │  │
│  │                                                                          │  │
│  │ ✓ Report generated successfully!                                        │  │
│  │                                                                          │  │
│  │ [👁️ Preview Report]                                                      │  │
│  │                                                                          │  │
│  │ NOTE: PDF download removed per user request. HTML preview only.         │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

COMPONENTS (ShadCN):
- Card: Checklist, team summary, next steps
- Button: "Generate Summary", "Preview Report", "Refresh Status"
- Progress: Generation progress bar
- Badge: Status indicators (✓ completed, ○ skipped, ⏳ in progress)
- Dialog: Full-screen HTML preview modal

INTERACTIONS:
- Auto-loads checklist status on page load
- Click "Refresh Status" → Re-fetches completion states
- Click "Generate Summary" → POST /api/v1/onboarding/generate-report
- Real-time progress updates via polling (not SSE)
- Click "Preview Report" → Opens HTML in dialog with print CSS
- Report remains accessible at /settings/onboarding-report

HTML REPORT STRUCTURE:
- Header: Team name, owner, date
- Section 1: Onboarding checklist (table with status/timestamp)
- Section 2: Team summary (KPIs, members, datasets)
- Section 3: Cost estimation breakdown
- Section 4: Business goals mapping results
- Section 5: Next steps recommendations
- Footer: Generated by Peter, timestamp, trace_id

BACKEND:
- POST /api/v1/onboarding/:team_id/generate-report
- Aggregates data from onboarding_progress, teams, cost_estimates, business_goals tables
- Uses Jinja2 template for HTML rendering
- Stores HTML in report_html field (no PDF generation per user request)
- Returns report_id for preview endpoint
- GET /api/v1/onboarding/:team_id/report → Returns HTML

PERSISTENCE:
- onboarding_reports table:
  - id, team_id, report_html (TEXT), generated_at, generated_by
- Accessible later from Settings → Onboarding Report

VALIDATION:
- At least 50% of steps must be completed to generate report
- Report generation can be skipped (optional step)
```

---

### 4.14 Step 12: Completion & Next Steps

**Celebrate setup completion and redirect to dashboard gallery.**

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│  Step 13 of 13: Setup Complete! 🎉                      [← Back]              │
│  Your team is ready to start creating dashboards                              │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│                         ┌─────────────────────┐                               │
│                         │   ✓ Setup Complete  │                               │
│                         │        🎉           │                               │
│                         └─────────────────────┘                               │
│                                                                                │
│  Congratulations, Sarah! Your team "Revenue Analytics Team" is all set up.    │
│                                                                                │
│  WHAT'S NEXT?                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                          │  │
│  │  1. EXPLORE YOUR DASHBOARD                                              │  │
│  │     View your generated dashboard: revenue-trends-dashboard             │  │
│  │     [📊 Open Dashboard →]                                                │  │
│  │                                                                          │  │
│  │  2. INVITE YOUR TEAM                                                    │  │
│  │     Add more members from Settings → Team Members                       │  │
│  │     [👥 Invite Members →]                                                │  │
│  │                                                                          │  │
│  │  3. CUSTOMIZE YOUR WORKSPACE                                            │  │
│  │     Edit layouts, add charts, or create new dashboards                  │  │
│  │     [✏️ Go to Dashboard Gallery →]                                       │  │
│  │                                                                          │  │
│  │  4. LEARN MORE                                                          │  │
│  │     Check out our documentation and best practices                      │  │
│  │     [📖 View Documentation →]                                            │  │
│  │                                                                          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  QUICK STATS                                                                   │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  ⏱️  Setup time: 12 minutes                                              │  │
│  │  🗂️  Tables discovered: 12                                               │  │
│  │  📊 Dashboards created: 1                                                │  │
│  │  👥 Team members: 4                                                      │  │
│  │  💰 Est. monthly cost: $57                                               │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ──────────────────────────────────────────────────────────────────────────── │
│                                                                                │
│  [🏠 Go to Dashboard Gallery]                      [⚙️ Open Settings]         │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

COMPONENTS (ShadCN):
- Card: Next steps with action buttons
- Button: Primary CTAs ("Open Dashboard", "Go to Dashboard Gallery")
- Badge: Quick stats KPIs
- Icon: Celebration checkmark

INTERACTIONS:
- Click "Open Dashboard" → Navigate to /dash/:slug
- Click "Invite Members" → Navigate to /settings/team
- Click "Go to Dashboard Gallery" → Navigate to /dashboards
- Click "View Documentation" → Opens docs in new tab
- Auto-redirect to gallery after 10s if no interaction

BACKEND:
- POST /api/v1/onboarding/:team_id/complete
- Marks onboarding_progress.completed = true, completed_at = now()
- Clears any in-progress flags
- Sends welcome email to team owner (optional, Phase 1)

ANALYTICS:
- Track completion event: "onboarding_completed"
- Attributes: team_id, duration_sec, steps_completed, dashboards_created
- Used for onboarding funnel analysis

POST-ONBOARDING:
- User can return to onboarding via Settings → Onboarding
- All steps remain editable (e.g., add more connections, re-run cost estimation)
- Completion status saved, but onboarding wizard hidden from primary nav
```

---

## Document Status

**Completion**: Phase 0 Onboarding Wireframes Complete
**Sections Added**:
- Auth (3): Login, OAuth Callback, Post-Auth Redirect
- Onboarding Layout Pattern
- Onboarding Steps 1-13 (Complete)
- Dashboard 3-Panel Layout
- Component Library (Buttons, Form Inputs)
- Responsive Patterns (Breakpoints, Layout Transformations)
- Accessibility Guidelines (Keyboard Nav, ARIA, Color Contrast)

**Last Updated**: 2025-10-31
**Status**: Ready for Phase 0 frontend & backend development

**Note**: Dashboard interface wireframes (Gallery, Editor tabs, Lineage views) can be added once Phase 0 onboarding is implemented and tested. The patterns established here (monotone theme, ShadCN components, responsive grid, accessibility requirements) apply throughout the application.
