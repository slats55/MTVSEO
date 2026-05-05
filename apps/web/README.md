# Web Dashboard

Next.js / React dashboard for the SEO Agent OS.

## Overview

Provides a clean, dark-themed UI for managing businesses, monitoring crawl jobs, viewing audit scores, browsing issues and opportunities, editing content, and reading reports.

## Tech Stack

- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS (dark professional theme)
- **State:** React Query (TanStack Query) for server state, Zustand for client state
- **Forms:** React Hook Form + Zod validation
- **Charts:** Recharts or Tremor for score visualization

## Structure

```
apps/web/
  src/
    app/            # Next.js App Router pages
    components/     # Reusable UI components
    features/       # Feature-scoped components (businesses, crawl, audit, etc.)
    lib/            # API client, utilities
    types/          # Shared TypeScript types
  public/           # Static assets
  tests/            # Jest / Playwright tests
```

## Getting Started

```bash
cd apps/web
npm install
npm run dev
```

Dashboard available at `http://localhost:3000`.
