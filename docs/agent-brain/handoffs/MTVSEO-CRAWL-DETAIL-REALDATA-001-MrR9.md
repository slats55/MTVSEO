# MTVSEO-CRAWL-DETAIL-REALDATA-001 — Mr.R9 Handoff

## Branch
- `feature/crawl-detail-realdata-001`
- Starting commit: `origin/feature/backend-phase2` (current HEAD)
- Ending commit: `7f2b446`

## Files Changed
- `apps/web/src/app/crawls/[id]/page.tsx` — new crawl detail page
- `apps/web/src/app/websites/[id]/page.tsx` — crawl rows made clickable (wrapped in Link)
- `apps/web/src/lib/queries/useCrawls.ts` — added `useCrawl(crawlId)` hook

## Crawl Detail Route
`/crawls/[id]` — real data via `GET /api/v1/crawls/{id}` (backend exists at `services/api/routers/crawls.py:50`)

## Hook Reused / Added
- `useCrawl(crawlId)` — NEW, uses `API_ROUTES.CRAWL_BY_ID(id)`, enabled when crawlId is truthy
- `useCrawl` reads from existing `CrawlRun` type (already defined in `apps/web/src/lib/api/types/crawls.ts`)
- `useWebsiteCrawls` — already existed, used on website detail page

## Backend Endpoint Confirmed
`GET /api/v1/crawls/{crawl_run_id}` exists at `services/api/routers/crawls.py:50-64`.
Returns `CrawlRunRead` schema with full fields: id, website_id, status, crawl_depth, max_pages, respect_robots, started_at, completed_at, pages_discovered, pages_crawled, error_message, created_at, updated_at.

## Related SEO Issues
Not included — API does not support filtering SEO issues by crawl_run_id on the detail page without a separate query per crawl run. The website detail page shows real SEO issues filtered client-side by crawl_run_id.

## Fake-Data Grep Result
```
apps/web/src/app/websites/[id]/page.tsx:242:  const crawls = data?.items ?? [];
```
This is a real variable name binding the API response's `items` array — NOT fake data. No other matches.

## Build Result
```
Route (app)                              Size     First Load JS
├ ƒ /crawls/[id]                         5.05 kB         117 kB
└ ƒ /websites/[id]                       4.47 kB         116 kB
```
✓ Compiled successfully — no errors, no fake data, no mock arrays.

## Known Limitations
- Related SEO issues not shown on crawl detail (API only supports crawl_run_id filter for SEO issues via client-side filter on the website page; no per-crawl detail linkout yet)
- No cancel action on detail page (crawl cancel endpoint exists at `POST /api/v1/crawls/{id}/cancel` but not wired to UI — reserved for future slice)

## Commit
`7f2b446` — pushed to `origin/feature/crawl-detail-realdata-001`