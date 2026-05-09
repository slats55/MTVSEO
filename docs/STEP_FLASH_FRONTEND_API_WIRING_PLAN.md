# Step Flash Frontend API Wiring Plan

## Context
- Stable base: `feature/backend-phase2`
- Stable commit: `4f78e73` — Merge Step Flash mock dashboard UI
- Current UI status: Dashboard shell with mock data (metrics, recent crawls, top issues, keyword opportunities)
- API contract status: Pending review of Ryzen 9's `docs/ryzen9-api-contract-for-frontend` branch

## Current Frontend Structure
- **Dashboard page**: `apps/web/src/app/page.tsx`
  - 4 metric cards (Technical SEO, GEO/AI Visibility, Content Quality, Crawl Health)
  - Quick action links (New Crawl, Run SEO Audit, Run GEO Audit, Generate Report)
  - Recent Crawls table (website, status, pages, score, date)
  - Top Issues list (severity, count, title, category)
  - Keyword Opportunities table (keyword, volume, difficulty, position, change)
- **Components**: `metric-card.tsx`, `status-badge.tsx`
- **State**: All data is hardcoded mock arrays; no API calls, no React Query
- **Styling**: Tailwind CSS, Lucide icons, dark theme

## Proposed API Client Structure
```
apps/web/src/lib/api/
├── client.ts           # fetch wrapper with base URL, error handling
├── routes.ts           # endpoint path constants
├── types/
│   ├── businesses.ts
│   ├── websites.ts
│   ├── crawls.ts
│   ├── pages.ts
│   └── common.ts       # pagination, enums (CrawlStatus, etc.)
└── hooks/              # optional: custom React Query hooks later
```

- **Base URL**: `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`)
- **Client**: lightweight `fetch` wrapper with JSON handling, error throwing, retry optional
- **Types**: aligned with backend Pydantic models; use `zod` for runtime validation if needed
- **Errors**: standard HTTP status handling; non-200 returns parsed error JSON or generic message

## Proposed React Query Structure
- **Query keys**:
  - `['businesses', { list? }]`
  - `['websites', { businessId? }]`
  - `['crawls', { websiteId? }]`
  - `['pages', { crawlId? }]`
  - `['page', { pageId }]`
  - `['pageByUrl', { url }]`
- **Mutations** (deferred):
  - `createCrawl`, `updateBusiness`, etc.

## Dashboard Data Mapping
| UI Section          | API Endpoint(s)                      | Notes                            |
|---------------------|--------------------------------------|----------------------------------|
| Metrics             | `GET /api/v1/pages/summary/{id}`?   | May need a dedicated dashboard summary endpoint; otherwise compute from crawls/pages |
| Recent Crawls       | `GET /api/v1/crawls/` (filter by business) | Sort by `started_at` desc, limit 4 |
| Top Issues          | Not in CRUD yet                      | Defer until audit/GEO endpoints exist |
| Keyword Opportunities| Not in CRUD yet                      | Defer until keyword research endpoints exist |

**Immediate minimum**: wire Recent Crawls from `GET /api/v1/crawls/`.

## Safe First Implementation Slice
1. Add `apps/web/src/lib/api/client.ts` (fetch wrapper)
2. Add `apps/web/src/lib/api/routes.ts` (path constants)
3. Add `apps/web/src/lib/api/types/crawls.ts` (Crawl, CrawlList response)
4. Update `apps/web/src/app/page.tsx`:
   - Replace `recentCrawls` with `useQuery(['crawls'], fetchCrawls)`
   - Keep `mock` fallback if query fails or empty
   - Loading state: skeleton or spinner
   - Do NOT add mutations
5. Verify build and dev server still work
6. Do not modify backend; assume `/api/v1/crawls/` returns `{ items: Crawl[], total: int }`

## Deferred Work
- Create/update/delete mutations (after read wiring stable)
- Authentication/session ownership (backend auth not yet productized)
- GSC integration frontend (separate slice)
- Reports page and export functionality
- Advanced SEO issue workflows (audit results page)
- Real-time updates via WebSocket/polling (later)

## Risks
- Backend authentication not productized — frontend may need to handle 401/403 gracefully
- No dashboard summary endpoint yet — metrics may require separate page-aggregation API
- Page/issue metrics could need aggregation endpoint rather than per-page data
- Local CORS/base URL setup may need environment-specific config
- React Query version compatibility (if already installed, check version)

## Recommended Next Prompt (After Ryzen 9 Contract Review)
```
Implement the first frontend API wiring slice:

1. Add React Query to the Next.js app (if not already installed):
   - `npm install @tanstack/react-query`
   - Create `apps/web/src/providers.tsx` with QueryClientProvider

2. Create API client:
   - `apps/web/src/lib/api/client.ts` with fetch wrapper using NEXT_PUBLIC_API_URL
   - `apps/web/src/lib/api/routes.ts` with endpoint constants
   - `apps/web/src/lib/api/types/crawls.ts` with types matching backend CRUD response

3. Add a hook `apps/web/src/lib/api/hooks/useCrawls.ts`:
   - `useQuery(['crawls'], fetchCrawls)`
   - Accept optional `websiteId` filter later

4. Update `apps/web/src/app/page.tsx`:
   - Import `useCrawls`
   - Replace mock `recentCrawls` with query data (limit 4, sorted by started_at desc)
   - Show loading state, error state, empty state
   - Keep StatusBadge mapping working with actual `CrawlStatus` enum

5. Do not add any mutations or other endpoints yet.

6. Verify: `npm run build` succeeds, `pytest tests/ -q` still passes.

Follow the API contract doc exactly for response shapes and status values. Do not modify backend code.
```
