# Step Flash Mock UI Slice

## Purpose
This frontend work was completed while Ryzen 9 MiniMax was still finalizing backend CRUD/API contracts. The goal was to improve the dashboard shell and user experience using mock data only, so the product looks more like a professional SEO SaaS app. No backend endpoints were wired; all data is local and mock.

## Branch Context

- **Base branch**: `feature/backend-phase2`
- **UI branch**: `feature/stepflash-dashboard-shell-mock-ui`
- **Backend branch intentionally not modified**: `origin/sync/ryzen9-minimax-latest`

## What Changed

Frontend files modified:
- `apps/web/src/app/page.tsx` — Completely redesigned dashboard with:
  - Reusable MetricCard component import
  - StatusBadge component for consistent status indicators
  - KPI cards grid with grades and trends
  - Quick actions grid with descriptions and chevron hints
  - Two-column layout: Recent Craws table + Top Issues panel
  - New Keyword Opportunities table with difficulty bars
  - Refresh button and "last sync" timestamp
  - Better visual hierarchy and grouping

New components:
- `apps/web/src/components/metric-card.tsx` — Reusable metric display card with grade colors, progress bar, trend indicator
- `apps/web/src/components/status-badge.tsx` — Consistent status badge with 5 variants (success, warning, error, info, neutral)
- `apps/web/src/lib/utils.ts` — Utility `cn` function for classnames (simplified; no tailwind-merge dependency)

Styling improvements:
- Dark slate theme preserved with blue accents
- Consistent spacing and typography
- Hover states and transitions
- Responsive grid layouts (1-col on mobile, 2-col sm, 4-col lg for KPIs)
- Accessible color contrast
- Icon usage from lucide-react for visual cues

## Mock Data Used

All data is hard-coded in `page.tsx`:
- `metrics` array for KPI cards
- `quickActions` for navigation grid
- `recentCrawls` for the crawls table (id, website, status, pages, score, date)
- `topIssues` for priority issues list
- `keywordOpportunities` for keyword table (volume, difficulty, position, change)

No API calls are made. The UI is ready to be connected to React Query later.

## Verification

- **npm install**: ✅ up to date (394 packages)
- **npm run build**: ✅ PASS (Next.js 14.2.15)
  - Compiled successfully, type checks passed
  - Static pages: `/`, `/_not-found`, `/audits`, `/businesses`, `/reports`
  - Size: First Load JS 91.5 kB for `/`
- **npm run lint**: Not run (interactive setup required; no `.eslintrc.json` present)
- **npm run typecheck**: Included in build; no errors
- **npm test**: Not defined

## Backend Dependencies Deferred

These must wait until Ryzen 9 CRUD branch passes Step Flash review:
- Real business CRUD API wiring (list, create, edit, delete)
- Website CRUD endpoints integration
- Crawl CRUD endpoints (trigger, status, results)
- Schema-driven form submission for business creation
- Live dashboard data fetching via React Query
- Authentication and user session handling
- Error boundary wiring to real error responses
- Optimistic updates for mutations

## Recommended Next Step

This branch is ready for review and should be merged into `feature/backend-phase2` **after** Ryzen 9's CRUD implementation branch is verified and merged. The UI improvements are independent and can coexist with backend API changes.

Once backend CRUD is stable:
1. Add React Query provider to `app/layout.tsx`
2. Create API service layer with `fetch` wrappers
3. Replace mock data with real queries/mutations
4. Implement "Add Business" modal with form
5. Add loading skeletons and error handling
6. Wire real-time updates for crawl status
