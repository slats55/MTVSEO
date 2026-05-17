# Handoff: MTVSEO-WEBSITE-CRAWLS-REALDATA-001
**Agent:** Mr.R9
**Date:** 2026-05-17
**Status:** COMPLETE

---

## Branch Info
- **Branch:** `feature/website-crawls-realdata-001`
- **Base:** `origin/feature/backend-phase2` (commit `4b31670`)
- **Start commit:** `4b31670` ("merge: integrate website detail real-data page")
- **End commit:** local HEAD (pre-push)

---

## Files Changed
1. `apps/web/src/app/websites/[id]/page.tsx` — modified to add crawl history section
2. `apps/web/src/lib/queries/useWebsiteCrawls.ts` — **new** hook for website-scoped crawl fetching

---

## Crawl Hook Reused / Added
- **Reused:** `useWebsite` (existing) — unchanged
- **Added:** `useWebsiteCrawls` — new hook in `apps/web/src/lib/queries/useWebsiteCrawls.ts`
  - Wraps `GET /api/v1/crawls/?website_id={id}&limit=10&skip=0`
  - Uses same `CrawlListResponse` type as `useCrawls`
  - `enabled: Boolean(websiteId)` — only runs when a real ID is present

---

## Crawl API Shape Observed
**Backend:** `services/api/routers/crawls.py`
- `GET /api/v1/crawls/` — supports optional `website_id` query param (UUID), `skip`, `limit`
- Returns `CrawlRunList` with `items: CrawlRun[]` and `total: int`
- `CrawlRun` fields: `id`, `website_id`, `status`, `crawl_depth`, `max_pages`, `respect_robots`, `started_at`, `completed_at`, `pages_discovered`, `pages_crawled`, `error_message`, `created_at`, `updated_at`
- `CrawlStatus`: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`

**Frontend types:** `apps/web/src/lib/api/types/crawls.ts`
- `CRAWL_STATUS_LABELS` and `CRAWL_STATUS_VARIANTS` maps already existed

---

## website_id Filtering
- **API-side filtering:** YES — `GET /api/v1/crawls/?website_id={uuid}` hits the backend filter at `crawls.py:36-38`
- **Client-side filtering:** N/A — API handles it
- No fake filtering; no hardcoded arrays

---

## Fake-Data Grep Result
```
$ grep -RInE "MOCK|mock|fake|sample|demo|mtvhvaccom|green-cultureco|countryroadsautocom|seoScore|geoScore|crawls\s*=\s*|const\s+crawls\s*=\s*|crawlRuns\s*=\s*|const\s+crawlRuns\s*=\s*" apps/web/src/app apps/web/src/lib

apps/web/src/app/websites/[id]/page.tsx:236:  const crawls = data?.items ?? [];
```
**Result: `NO_FAKE_CRAWL_DATA_FOUND`** (line 236 is real data destructuring from API response, not fake data)

---

## Build Result
```
cd apps/web && npm install && npm run build
✓ Compiled successfully
✓ First Load JS shared by all — 87.1 kB
Route /websites/[id] — 3.57 kB, 115 kB first load
✓ No type errors
✓ No build artifacts committed
```

---

## Known Limitations
1. `useWebsiteCrawls` does not invalidate when new crawls are triggered — the page will show stale data until refresh. Follow-up work could add `useCreateCrawl` invalidation to `queryClient.invalidateQueries`.
2. No pagination controls in the crawl history section — shows up to 10 most recent crawls. If total > 10, only the 10 most recent are displayed with no "load more" UI.
3. No link from individual crawl row to a crawl detail page — no `/crawls/[id]` route exists yet.

---

## Commit & Push
```
git add .
git commit -m "feat: show real crawl history on website detail"
git push origin feature/website-crawls-realdata-001
```

**Branch is ready for Mr.R7 verification and Commander GO/NO-GO.**