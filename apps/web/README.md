# Peter Web Application

Modern Next.js 15 frontend for the Peter dashboard platform with a three-panel VS Code-inspired layout.

## Features

- **Three-Panel Layout**: Explorer (datasets & YAML) | Workspace (dashboard view/edit) | Assistant (AI chat)
- **View/Edit Modes**: Toggle between viewing dashboards and editing them
- **Real-time YAML Editing**: Edit YAML directly with live validation
- **Chart Visualization**: Recharts-powered charts (KPI, Line, Bar, Area)
- **Freshness Indicators**: Visual indicators showing data recency
- **Monotone Theme**: Clean black/white/grey design system
- **Responsive Design**: Resizable panels with collapsible sidebars
- **State Management**: Zustand for global state, TanStack Query for server state

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **UI Library**: ShadCN/UI + Radix UI
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State**: Zustand + TanStack Query
- **Type Safety**: TypeScript

## Getting Started

### Prerequisites

- Node.js >= 18.17.0
- pnpm >= 8.0.0

### Installation

```bash
# From root directory
pnpm install

# Or from apps/web
cd apps/web
pnpm install
```

### Development

```bash
# Start dev server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Run type checking
pnpm typecheck

# Run linting
pnpm lint
```

### Environment Variables

Copy `.env.local.example` to `.env.local` and configure:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_ENABLE_ASSISTANT=true
```

## Project Structure

```
apps/web/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout with providers
│   ├── page.tsx           # Home page (main app shell)
│   └── globals.css        # Global styles
├── components/
│   ├── layout/            # App shell and panel components
│   │   ├── app-shell.tsx  # Main three-panel layout
│   │   ├── app-header.tsx # Top header with controls
│   │   ├── left-panel.tsx # Explorer panel
│   │   ├── center-panel.tsx # Workspace panel
│   │   └── right-panel.tsx # Assistant panel
│   ├── dashboard/         # Dashboard-specific components
│   │   ├── dashboard-view.tsx
│   │   └── dashboard-editor.tsx
│   ├── datasets/          # Dataset browser
│   │   └── dataset-browser.tsx
│   ├── yaml/              # YAML viewer/editor
│   │   └── yaml-viewer.tsx
│   ├── charts/            # Chart components
│   │   ├── chart-card.tsx
│   │   ├── kpi-card.tsx
│   │   ├── line-chart.tsx
│   │   └── bar-chart.tsx
│   └── ui/                # ShadCN UI components
├── hooks/                 # Custom React hooks
│   └── use-dashboards.ts  # Dashboard data hooks
├── lib/
│   ├── utils.ts           # Utility functions
│   ├── store.ts           # Zustand global state
│   ├── query-client.ts    # TanStack Query config
│   └── api-client.ts      # API client wrapper
├── providers/             # React context providers
│   ├── query-provider.tsx
│   └── theme-provider.tsx
├── types/                 # TypeScript types
│   └── dashboard.ts
└── styles/
    └── globals.css        # Global CSS with custom properties
```

## Key Components

### App Shell

The main three-panel layout with resizable panels:

- **Left Panel**: Dataset browser (top) + YAML viewer (bottom)
- **Center Panel**: Dashboard workspace with view/edit tabs
- **Right Panel**: AI assistant chat interface

### View/Edit Modes

- **View Mode**: Read-only dashboard view with refresh controls
- **Edit Mode**: Three tabs (Dashboard, YAML, Preview) for editing

### State Management

- **Global State**: Zustand store for UI state, dashboard state, and chat
- **Server State**: TanStack Query for API calls with caching
- **Dirty State**: Tracks unsaved changes with confirmation dialogs

## Development Guidelines

### Monotone Theme

Follow the strict black/white/grey color palette:

- Background tones: `bg-primary`, `bg-secondary`, `bg-tertiary`
- Text tones: `text-primary`, `text-secondary`, `text-tertiary`
- Use semantic colors (`success`, `warning`, `error`) only for data/status

### Component Patterns

1. **Use ShadCN components** for all UI primitives
2. **Follow compound component pattern** for complex components
3. **Implement loading skeletons** for async data
4. **Add error boundaries** for graceful failures
5. **Use React.memo** for expensive chart renders

### Performance

- Code splitting at route level
- Lazy loading for heavy components
- Optimized bundle size (target: < 200 KB)
- Debounced YAML validation
- Virtualized lists for large datasets (future)

## Testing

```bash
# Unit tests
pnpm test

# E2E tests
pnpm test:e2e

# E2E with UI
pnpm test:e2e --headed
```

## Deployment

The app is designed to deploy to Cloud Run alongside the FastAPI backend:

```bash
# Build production bundle
pnpm build

# Docker build (if using containerization)
docker build -t peter-web .
```

## Contributing

1. Follow the monotone theme strictly
2. Use TypeScript for all new files
3. Add tests for new features
4. Run `pnpm typecheck` and `pnpm lint` before committing
5. Keep bundle size under budget

## License

Private - Internal use only
