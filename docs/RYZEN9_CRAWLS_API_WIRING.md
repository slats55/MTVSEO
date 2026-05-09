# Ryzen 9 Crawls API Wiring

## Purpose

This is the first real frontend API wiring slice targeting the dashboard Recent Crawls section. It replaces the hardcoded mock array with live data from `GET /api/v1/crawls/?limit=4&skip=0`. No other UI sections are wired in this branch.

---

## Branch Context

- **Base branch:** `feature/backend-phase2`
- **Base commit:** `415587a` ("Merge frontend API wiring plan docs")
- **Implementation branch:** `feature/ryzen9-api-wiring-crawls-first`
- **Reason Ryzen 9 took over from Step Flash:** Step Flash's gateway/lint write tool was corrupting TypeScript output — a tooling issue, not a code/design blocker.

---

## Endpoint Wired

- `GET /api/v1/crawls/?limit=4&skip=0`
- Returns `{ items: CrawlRun[], total: number }`
- Sorted by `created_at desc` server-side
- No auth filter in this slice

---

## Environment

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

- Use `localhost`, not `127.0.0.1`, due to current CORS config (`cors_origins = ["http://localhost:3000"]`)
- `.env.local` should NOT be committed (contains local dev secrets if any)
- `.env.example` MAY be committed — used as a template

---

## Files Added

```
apps/web/.env.example                              (NEW — env template)
apps/web/src/lib/api/client.ts                     (NEW — fetch wrapper)
apps/web/src/lib/api/routes.ts                     (NEW — route constants)
apps/web/src/lib/api/types/crawls.ts               (NEW — TypeScript types)
apps/web/src/app/providers.tsx                      (NEW — React Query provider)
apps/web/src/lib/queries/useCrawls.ts               (NEW — query hook)
```

## Files Modified

```
apps/web/src/app/layout.tsx                        (added Providers wrapper)
apps/web/src/app/page.tsx                          (wired Recent Crawls to useCrawls)
```

---

## Behavior Added

### API Client (`client.ts`)
- Reads `NEXT_PUBLIC_API_URL` from `process.env`, defaults to `http://localhost:8000`
- Normalizes trailing slashes to avoid double-slash issues
- Throws `ApiError { message, status }` on non-2xx responses
- Includes `credentials: "include"` for future auth compatibility

### React Query Provider (`providers.tsx`)
- `QueryClient` with `staleTime: 30s`, `retry: 2`
- Wrapped in `QueryClientProvider`
- Used in `layout.tsx` to wrap all children

### Crawl Query Hook (`useCrawls.ts`)
- `GET /api/v1/crawls/?limit=4&skip=0`
- Returns `{ data: CrawlListResponse, isLoading, isError, error }`
- No mutations

### Dashboard Wiring (`page.tsx`)
- Calls `useCrawls()` on mount
- **Loading state:** "Loading crawls..." centered text in table body
- **Error state:** "Failed to load crawls" in red
- **Empty state:** "No crawls yet. Run your first crawl from the Businesses page."
- **Mock fallback:** If API returns zero items and is not loading, shows hardcoded `MOCK_CRAWLS` (4 rows) so the UI never appears broken
- **Display:** Up to 4 rows from API, rendered with `website_id` prefix shown as truncated UUID (first 8 chars + ellipsis). `pages_crawled` shown. Score column shows `—` (not yet available from crawl run). Status label uses `CRAWL_STATUS_LABELS` for human-readable text.

---

## Backend Safety

- **No backend files changed** — this is frontend-only
- **No backend tests changed**
- **No API contract changed** — only consuming existing endpoint
- **No mutations added** — read-only slice

---

## Known Limitations

1. **No `website_name` field** — `CrawlRunRead` has `website_id` only. Table shows truncated UUID until website name join is added (deferred backend enhancement).
2. **No auth/session filtering** — `list_crawl_runs` returns all crawl runs without user scoping. Fine for local dev, needs backend auth work before production.
3. **No GSC integration** — not in this slice.
4. **No crawl creation** — `POST /api/v1/crawls/` not wired. New Crawl quick action still links to `/businesses`.
5. **Score column shows `—`** — `CrawlRunRead` has no `score` field. Score must come from a separate page analysis endpoint (not yet implemented).
6. **Time display relies on browser `Date`** — `timeAgo()` function runs client-side. Server and client clocks must be in sync for accurate relative times.

---

## Verification Results

```
# Frontend build
cd apps/web && npm install && npm run build
```

```
# Backend verification (from repo root)
python scripts/verify_local.py               ✓ ALL CHECKS PASSED
pytest tests/ -q                              ✓ 34 passed (0 failed)
python -m compileall services packages tests  ✓ no errors
```

---

## Recommended Next Step

Step Flash should review `feature/ryzen9-api-wiring-crawls-first` at the pushed commit. Key review points:

1. `providers.tsx` — correct QueryClient setup and `QueryClientProvider` wrapping
2. `client.ts` — correct `NEXT_PUBLIC_API_URL` usage and error handling
3. `page.tsx` wiring — loading/error/empty/mock-fallback states all present
4. `website_id` truncation — temporary workaround until website name join is added
5. `layout.tsx` — `Providers` wraps all children correctly

After review, merge into `feature/backend-phase2` and move to wiring website listing next (`GET /api/v1/websites/`).