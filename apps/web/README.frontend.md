# Peter Dashboard Platform - Frontend

Next.js 15 frontend application for the Peter dashboard platform.

## Tech Stack

- **Framework**: Next.js 16.0.1 (App Router)
- **React**: React 19.2.0
- **TypeScript**: 5.9.3
- **Styling**: Tailwind CSS 4.1.16 with monotone theme
- **UI Components**: ShadCN/UI (Neutral palette)
- **State Management**: Zustand 5.0.8
- **Data Fetching**: TanStack Query 5.90.5
- **Charts**: Recharts 3.3.0
- **Icons**: Lucide React
- **Fonts**: Inter Variable

## Project Structure

```
apps/web/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   │   └── ui/          # ShadCN UI components
│   ├── lib/             # Utilities and helpers
│   └── styles/          # Global styles
├── public/              # Static assets
└── tests/               # Test files
```

## Development

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Run production server
pnpm start

# Type checking
pnpm typecheck

# Linting
pnpm lint
```

## Environment Variables

Copy `.env.local.example` to `.env.local` and configure:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=your-client-id
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Design System

### Monotone Color Palette

Strict black/white/grey theme:
- Background: #FFFFFF (light) / #0A0A0A (dark)
- Text: #0A0A0A (light) / #FAFAFA (dark)
- Semantic colors (data only): Success, Warning, Error, Neutral

### Typography

- Font: Inter Variable
- H1: 32px / 600 weight
- H2: 24px / 600 weight
- Body: 16px / 400 weight
- Small: 14px / 400 weight

### Spacing Scale

4px, 8px, 16px, 24px, 32px, 48px

## Features Implemented

### Phase 1: Foundation ✅
- [x] Next.js 15 App Router setup
- [x] Tailwind CSS with monotone theme
- [x] ShadCN/UI components
- [x] Core dependencies (TanStack Query, Zustand, Recharts)
- [x] API proxy configuration
- [x] Environment configuration

### Phase 2: OpenAPI Client & Auth (In Progress)
- [ ] OpenAPI TypeScript client generation
- [ ] Google OAuth authentication
- [ ] Session management
- [ ] App shell layout

## Next Steps

1. Wait for backend OpenAPI spec
2. Generate TypeScript client
3. Implement authentication layer
4. Build app shell (3-panel layout)
5. Create chart components

## Documentation

- Frontend PDR: `/docs/frontend_pdr.md`
- UI Design System: `/docs/ui_pdr.md`
- Project Guidelines: `/CLAUDE.md`
- Task Tracking: `/docs/task.md`
