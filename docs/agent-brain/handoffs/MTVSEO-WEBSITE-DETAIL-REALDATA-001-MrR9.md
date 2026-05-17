# MTVSEO-WEBSITE-DETAIL-REALDATA-001 — Mr.R9 Build Handoff

## Branch
`feature/website-detail-realdata-001`

## Commits
- **Starting commit**: `9e5b463` (merge: integrate websites page real-data wiring)
- **Ending commit**: `03e221c` (feat: add real-data website detail page)
- **1 commit total**

## Files Changed
```
.gitignore                                           (lib/ → build/lib/ build/lib64/)
apps/web/src/app/websites/page.tsx                    (added Link + ChevronRight to rows)
apps/web/src/app/websites/[id]/page.tsx              (new — detail page)
apps/web/src/lib/queries/useWebsite.ts               (new — useWebsite(id) hook)
```

## Backend Endpoint
- `GET /api/v1/websites/{website_id}` — **CONFIRMED** in `services/api/routers/websites.py` (lines 50-64)
- Response schema: `WebsiteRead` — fields: `id, business_id, url, name, created_at, updated_at`
- No backend changes were required or made

## Hook / Type Added
- **New**: `apps/web/src/lib/queries/useWebsite.ts` — `useWebsite(id: string)` hook
  - Reuses `Website` type from `@/lib/api/types/websites`
  - Reuses `apiGet` from `@/lib/api/client`
  - Reuses `API_ROUTES.WEBSITE_BY_ID(id)` route helper
  - `enabled: !!id` prevents fetching on empty ID

## Related Crawls
- NOT included on the detail page
- `GET /api/v1/crawls/?website_id={id}` IS confirmed supported by the backend (crawls router, line 25-38)
- No `useCrawlsForWebsite(id)` hook exists and no dedicated detail-page crawl list was in scope
- A plain-text note is shown at the bottom of the detail page pointing to the API contract

## States Implemented
- Loading: `Loader2` spinner, centered
- Error: `AlertCircle` + backend message
- Not-found / unavailable: explicit `if (!data)` guard before render
- Success: fields table with all real backend fields

## Real Fields Shown
- id, business_id, url, name (if set), created_at, updated_at

## Build Result
```
cd apps/web && npm install && npm run build
✓ Compiled successfully — all types clean
Route (app): ƒ /websites/[id]   (Dynamic, server-rendered on demand)
```

## Fake-Data Grep
```
grep -RInE "MOCK|mock|fake|sample|demo|mtvhvaccom|green-cultureco|countryroadsautocom|seoScore|geoScore" apps/web/src/app apps/web/src/lib
→ NO_FAKE_DETAIL_DATA_FOUND
```

## Known Limitations
- Related crawl runs not shown on the detail page (no hook + no dedicated UI in scope)
- No edit/update website flow
- No delete website flow

## Push Status
Branch pushed to `origin/feature/website-detail-realdata-001` — confirmed

## Commit Hash
`03e221c`