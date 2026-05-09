# Ryzen 9 Post-Merge Crawls API Verification

## Context

- **Stable branch:** `feature/backend-phase2`
- **Latest commit:** `660ed54` ("Merge crawls API wiring for dashboard")
- **Step Flash review verdict:** PASS WITH NOTES (backend pytest collection failures on Step Flash were environment-related, not code failures — confirmed by running pytest locally on Ryzen 9)
- **Purpose:** Verify that the merged crawls API wiring is correct and the backend contract matches the frontend expectations before proceeding to websites wiring

---

## Verification Results

### python scripts/verify_local.py

```
✓ ALL CHECKS PASSED — repo is ready for Codex
  - Python 3.12 >= 3.11
  - All required dependency imports (fastapi, uvicorn, sqlalchemy, pydantic, httpx, etc.)
  - All package exports importable
  - FastAPI app imports cleanly
  - /health returns 200
  - DATABASE_URL configured
```

### pytest tests/ -q

```
34 passed in 1.96s
```

All 34 tests passed. Tests cover businesses, websites, and crawls CRUD endpoints.

### python -m compileall

```
Clean compile — no syntax errors in services/, packages/, tests/
```

---

## Crawls Endpoint Contract

### GET /api/v1/crawls/

**Route confirmed in app route map:**

```
GET  /api/v1/crawls/  list_crawl_runs
```

**Query parameters supported:**

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `skip` | int (>=0) | 0 | offset for pagination |
| `limit` | int (1-100) | 20 | page size |
| `website_id` | UUID (optional) | null | filter by website |

**Frontend call:** `GET /api/v1/crawls/?limit=4&skip=0` — fully supported.

**Response shape (CrawlRunList):**

```json
{
  "items": [
    {
      "id": "uuid",
      "website_id": "uuid",
      "status": "PENDING|RUNNING|COMPLETED|FAILED|CANCELLED",
      "crawl_depth": 3,
      "max_pages": 50,
      "respect_robots": true,
      "started_at": "datetime | null",
      "completed_at": "datetime | null",
      "pages_discovered": 0,
      "pages_crawled": 0,
      "error_message": "string | null",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": 0
}
```

**Empty response behavior:** `{"items": [], "total": 0}`

---

## Frontend Contract Match

### Frontend files inspected

| File | Status |
|------|--------|
| `apps/web/src/lib/api/client.ts` | NEXT_PUBLIC_API_URL used; default `http://localhost:8000` |
| `apps/web/src/lib/api/routes.ts` | CRAWLS: "/api/v1/crawls/" — matches backend |
| `apps/web/src/lib/api/types/crawls.ts` | TypeScript `CrawlRun` matches `CrawlRunRead` exactly; `CrawlListResponse` matches `CrawlRunList` |
| `apps/web/src/lib/queries/useCrawls.ts` | Calls `apiGet("${API_ROUTES.CRAWLS}?limit=4&skip=0")` — no mutations, GET only |
| `apps/web/src/app/page.tsx` | Reads `data?.items`, renders loading/error/empty states; falls back to mock MOCK_CRAWLS on empty/error |
| `apps/web/src/app/providers.tsx` | Minimal React Query setup (QueryClient, staleTime: 30s, retry: 2) |
| `apps/web/src/app/layout.tsx` | Wraps with `<Providers>` |
| `apps/web/.env.example` | `NEXT_PUBLIC_API_URL=http://localhost:8000` |
| `.gitignore` | `.env.local` is ignored — not tracked |

### Field-level match

| Frontend expects | Backend provides | Match |
|-----------------|------------------|-------|
| `id` | `id` (UUID) | ✓ |
| `website_id` | `website_id` (UUID) | ✓ |
| `status` | `status` (string enum) | ✓ |
| `started_at` | `started_at` (datetime\|null) | ✓ |
| `completed_at` | `completed_at` (datetime\|null) | ✓ |
| `pages_crawled` | `pages_crawled` (int) | ✓ |
| `created_at` | `created_at` (datetime) — fallback in UI | ✓ |

The UI uses `started_at` as primary date, falling back to `created_at` if null — both fields are provided by the backend.

**Response shape match:** `{ items: [...], total: number }` — exact match.

**No mutations added:** Frontend only uses `apiGet` — no POST/PUT/PATCH/DELETE.

---

## Risks / Notes

1. **Step Flash environment issue:** The pytest collection failures on Step Flash's machine were due to missing Python environment dependencies (fastapi, pydantic, etc. not installed in the test environment), not code failures. Confirmed by local Ryzen 9 run where all 34 tests pass cleanly.

2. **No pagination UI in frontend:** The frontend calls `?limit=4&skip=0` which is correct for the "Recent Crawls" widget. No pagination controls exist in the UI yet, but the backend supports it.

3. **No website_name in crawl list:** The crawl list returns `website_id` (UUID) but the UI displays it as a truncated mono string (`crawl.website_id.slice(0, 8)…`). A future enhancement could include a JOIN to surface the website URL/name. Not a mismatch — intentional trade-off for this slice.

4. **No auth on backend:** The crawls endpoint currently has no authentication/authorization. This is consistent with the current phase2 scope (CRUD wiring without auth). Auth is a future phase.

---

## Final Verdict

**VERIFIED — backend and frontend contract match.**

- `GET /api/v1/crawls/?limit=4&skip=0` returns the correct shape
- All fields the frontend uses are present or safely nullable
- No mutations were introduced
- React Query setup is minimal and correct
- Loading, error, empty, and fallback states all present
- All 34 tests pass on Ryzen 9
- No implementation files were modified; only a verification doc will be committed