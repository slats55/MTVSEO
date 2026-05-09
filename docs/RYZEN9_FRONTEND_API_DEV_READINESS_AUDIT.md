# Ryzen 9 Frontend API Dev Readiness Audit

## Purpose

This audit supports Step Flash's first frontend API wiring slice for `GET /api/v1/crawls/` into the `apps/web/src/app/page.tsx` Recent Crawls table. It checks CORS, local dev URL configuration, endpoint readiness, OpenAPI availability, and likely integration problems Step Flash may encounter.

**Important:** Step Flash's implementation branch (`feature/stepflash-api-wiring-crawls-first`) was intentionally NOT touched in this audit.

---

## Branch Context

- **Base branch:** `feature/backend-phase2`
- **Base commit:** `415587a` ("Merge frontend API wiring plan docs")
- **Audit branch:** `audit/ryzen9-frontend-api-dev-readiness`
- **Step Flash implementation branch:** `feature/stepflash-api-wiring-crawls-first` — not touched

---

## Baseline Verification

```
python scripts/verify_local.py               ✓ ALL CHECKS PASSED
pytest tests/                                 ✓ 34 passed (0 failed)
python -m compileall services packages tests  ✓ no errors
```

---

## Current Route Map

```
GET       /api/v1/businesses/                          list_businesses
POST      /api/v1/businesses/                          create_business
GET       /api/v1/businesses/{business_id}             get_business
PATCH     /api/v1/businesses/{business_id}             update_business
DELETE    /api/v1/businesses/{business_id}             delete_business

GET       /api/v1/websites/                            list_websites
POST      /api/v1/websites/                            create_website
GET       /api/v1/websites/{website_id}               get_website
PATCH     /api/v1/websites/{website_id}               update_website
DELETE    /api/v1/websites/{website_id}               delete_website

GET       /api/v1/crawls/                              list_crawl_runs         ← STEP FLASH TARGET
POST      /api/v1/crawls/                              trigger_crawl
GET       /api/v1/crawls/{crawl_run_id}               get_crawl_run
POST      /api/v1/crawls/{crawl_run_id}/cancel        cancel_crawl_run
GET       /api/v1/crawls/{crawl_run_id}/status        get_crawl_run_status

GET       /api/v1/pages/                                list_pages
GET       /api/v1/pages/{page_id}                      get_page
GET       /api/v1/pages/summary/{page_id}             get_page_summary
GET       /api/v1/pages/by-url/                        get_page_by_url

GET       /health                                      health_check
GET       /docs                                        Swagger UI
GET       /redoc                                       ReDoc
GET       /openapi.json                                OpenAPI spec
```

---

## CORS Readiness

**Status: CONFIGURED — READY FOR LOCAL DEV**

The backend configures `CORSMiddleware` in `services/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,   # ← loaded from settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Settings are in `services/api/config.py`:

```python
cors_origins: list[str] = ["http://localhost:3000"]
```

**Current CORS configuration:**
- `http://localhost:3000` — **ALLOWED** (Next.js default dev server port)
- `http://127.0.0.1:3000` — **NOT in the list** — potential issue if browser uses 127.0.0.1 instead of localhost
- `allow_credentials: True` — cookies/auth headers can be sent cross-origin
- `allow_methods: ["*"]` and `allow_headers: ["*"]` — all HTTP methods and headers permitted

**Step Flash CORS notes:**
- If testing from `http://127.0.0.1:3000`, add that to `cors_origins` in `.env` or config — but this is a backend config change, not a frontend change
- For local dev, using `http://localhost:3000` is the correct URL and it is already whitelisted
- CORS preflight requests are handled automatically by FastAPI's CORSMiddleware
- No `Access-Control-Allow-Origin: *` conflict since `allow_credentials=True` requires explicit origins

---

## Local API Base URL

**Backend expected at:** `http://localhost:8000`

The backend runs with uvicorn/FastAPI default. No `.env` is required to start locally — defaults in `services/api/config.py`:

```python
database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/seo_agent_os"
redis_url: str = "redis://localhost:6379/0"
cors_origins: list[str] = ["http://localhost:3000"]
```

**Frontend `.env.local` expected variable:** `NEXT_PUBLIC_API_URL=http://localhost:8000`

This variable is not currently present in `apps/web/.env.local` (no `.env.local` exists yet). Step Flash should create:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Why `NEXT_PUBLIC_` prefix:** Next.js strips server-only env vars from client bundles. Since the API URL is used in browser/client-side code, `NEXT_PUBLIC_API_URL` is required. Without it, the frontend will use whatever default the client.ts chooses (likely `http://localhost:8000` hardcoded, which is acceptable for local dev).

---

## Crawl Endpoint Readiness

### `GET /api/v1/crawls/` — `list_crawl_runs`

**Implementation** (`services/api/routers/crawls.py`):

```python
@router.get("/crawls/", response_model=CrawlRunList, status_code=status.HTTP_200_OK)
async def list_crawl_runs(
    website_id: UUID | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CrawlRunList:
```

**Response model:**
```python
class CrawlRunList(BaseModel):
    items: list[CrawlRunRead]
    total: int
```

**`CrawlRunRead` fields:**
```python
{
  "id": "uuid",
  "website_id": "uuid",
  "status": "PENDING|RUNNING|COMPLETED|FAILED|CANCELLED",
  "crawl_depth": 3,
  "max_pages": 50,
  "respect_robots": true,
  "started_at": "datetime|null",
  "completed_at": "datetime|null",
  "pages_discovered": 0,
  "pages_crawled": 0,
  "error_message": "string|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Endpoint capabilities:**
| Feature | Support | Notes |
|---------|---------|-------|
| Filter by `website_id` | Yes | `?website_id=<uuid>` |
| Pagination (`skip`, `limit`) | Yes | `skip` 0-indexed, `limit` max 100, defaults 0/20 |
| Sort | Desc by `created_at` | `query.order_by(CrawlRun.created_at.desc())` |
| Empty DB response | Clean | Returns `{"items": [], "total": 0}` |

**Frontend recommendations for Step Flash:**
1. **No `website_id` filter needed** for the Recent Crawls table on the main dashboard — show all crawls sorted by newest first
2. **Limit to 4** using `?limit=4` for the Recent Crawls UI (the mock shows 3 items, max 4 is reasonable)
3. **Sort is handled server-side** — newest first, no client sort needed
4. **Empty state** — if `items` is `[]`, render an empty table row or "No crawls yet" message. Do not crash.
5. **The Recent Crawls mock uses `website` name** — `crawl_run` doesn't include website URL/name directly. Step Flash needs to either:
   - Map `crawl_run.website_id` → fetch website name separately via `GET /api/v1/websites/{website_id}`
   - Or accept that the frontend shows only the `website_id` UUID in the table until website detail wiring is added

**Important:** `CrawlRunRead` does NOT include `website_url` or `website_name` — only `website_id`. This is a schema gap. The mock dashboard shows `mtvhvac.com` etc. Step Flash should document this gap rather than assume the backend returns website names in the crawl run response.

---

## OpenAPI / Docs Availability

**Available and ready to use:**

| URL | Purpose | Auth |
|-----|---------|------|
| `http://localhost:8000/docs` | Swagger UI | None (local) |
| `http://localhost:8000/redoc` | ReDoc | None (local) |
| `http://localhost:8000/openapi.json` | Raw OpenAPI JSON | None (local) |

Step Flash should open `http://localhost:8000/docs` in a browser tab while wiring to:
- See exact request/response schemas
- Copy JSON examples
- Verify the `/api/v1/crawls/` response shape before writing TypeScript types
- Test the endpoint directly from the browser during debugging

---

## Local Dev Commands

### Backend

```bash
# Terminal 1 — from project root
cd /home/mtv/Projects/seo-agent-os
source .venv/bin/activate
uvicorn services.api.main:app --reload --port 8000
```

**Prerequisites:**
- PostgreSQL running at `localhost:5432` (or `DATABASE_URL` updated in `.env`)
- Redis running at `localhost:6379` (or `REDIS_URL` updated in `.env`)
- `.env` file with `DATABASE_URL` and `REDIS_URL` if non-default

**Verify backend is up:**
```bash
curl http://localhost:8000/health
# → {"status":"healthy","app":"seo-agent-os",...}
```

**Verify CORS headers:**
```bash
curl -I http://localhost:8000/api/v1/crawls/ -H "Origin: http://localhost:3000"
# → Should include: Access-Control-Allow-Origin: http://localhost:3000
```

### Frontend

```bash
# Terminal 2 — from apps/web/
cd /home/mtv/Projects/seo-agent-os/apps/web
npm run dev
# → Local: http://localhost:3000
```

**Prerequisites:**
- `NEXT_PUBLIC_API_URL=http://localhost:8000` in `apps/web/.env.local`
- Node.js 20+, npm installed

**No `.env.local` exists yet** — Step Flash must create it:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Integration Risks For Step Flash

### Risk 1: `website_id` is a UUID, not a website name
- **Severity:** Medium
- **Problem:** `CrawlRunRead` has no `website_url` or `website_name` field. The mock dashboard shows `mtvhvac.com`. Step Flash cannot render website names without a separate `GET /api/v1/websites/{website_id}` call.
- **Mitigation:** For the first wiring slice, Step Flash can either (a) show `website_id` UUID in the table, or (b) fetch all websites once and map in-memory, or (c) accept showing "N/A" until the website detail slice is wired.
- **Fix:** Backend could add `website` as a joined relationship in the `CrawlRunRead` schema — deferred enhancement.

### Risk 2: Empty database returns `[]`
- **Severity:** Low
- **Problem:** Fresh DB with no crawl runs returns `{"items": [], "total": 0}`. The frontend needs to handle this gracefully — not show an error or blank page.
- **Mitigation:** React Query `data` will be `{items: [], total: 0}`. Render a "No crawls yet" empty state.

### Risk 3: `http://127.0.0.1:3000` vs `http://localhost:3000`
- **Severity:** Low
- **Problem:** `cors_origins` only lists `http://localhost:3000`. If the browser or OS resolves `localhost` to `127.0.0.1`, CORS may still work due to DNS rebinding, but it's inconsistent.
- **Mitigation:** Use `http://localhost:3000` explicitly in the browser. If 127.0.0.1 is needed, backend config change required.

### Risk 4: No auth/session context in crawl response
- **Severity:** Medium
- **Problem:** `list_crawl_runs` has no auth check — all crawl runs are returned to any caller. The `user_id` field on `CrawlRun` is not used to filter. This is fine for local dev but will need backend auth work before production.
- **Mitigation:** Step Flash should wire the endpoint without auth assumptions for now. Document in the PR that auth filtering is deferred.

### Risk 5: Backend not running
- **Severity:** Low (process issue)
- **Problem:** If Step Flash tries to run the frontend before starting the backend, API calls fail silently (React Query `error` state).
- **Mitigation:** Start backend first (`uvicorn services.api.main:app`). Confirm `curl http://localhost:8000/health` returns healthy before running `npm run dev`.

### Risk 6: `limit=4` for Recent Crawls is not a documented behavior
- **Severity:** Low
- **Problem:** The mock dashboard shows 3 recent crawls. Using `?limit=4` is a client-side choice. The backend has no "recent N" concept — it returns all sorted by `created_at desc`.
- **Mitigation:** Use `?limit=4` client-side to avoid over-fetching. The backend supports it.

### Risk 7: UUID serialization in JSON
- **Severity:** Low
- **Problem:** UUIDs are serialized as hyphenated strings in JSON responses. Next.js/TypeScript `fetch` returns them as strings — this is expected and correct.
- **Mitigation:** No special handling needed. Store UUIDs as strings.

---

## Recommended Fixes, If Any

| Issue | Recommendation | Priority |
|-------|---------------|----------|
| `http://127.0.0.1:3000` not in CORS origins | Docs-only note to use `localhost:3000` | Low |
| No `website_name` in `CrawlRunRead` | Deferred — backend enhancement needed | Medium |
| No auth filtering on `list_crawl_runs` | Deferred — auth middleware work needed | Medium |
| No `.env.local` for frontend | Step Flash creates it as part of wiring | Low |
| `CrawlRunRead` missing joined `website` data | Deferred — schema enhancement | Medium |

**Overall: NO backend code changes required for Step Flash to proceed with wiring `GET /api/v1/crawls/`.** All findings are either docs-only, deferred schema enhancements, or process notes.

---

## Final Verdict

**READY WITH NOTES**

Frontend wiring of `GET /api/v1/crawls/` can proceed immediately. The endpoint is functional, CORS is correctly configured for `http://localhost:3000`, and the response shape is stable. The main caveat is that `CrawlRunRead` does not include `website` relationship data, so Step Flash will need a workaround (separate website fetch or in-memory mapping) to show human-readable website names instead of UUIDs in the Recent Crawls table. This is documented as a deferred backend enhancement, not a blocker.

---

## Appendix: CrawlRunList Response Shape (for Step Flash types)

```json
// GET /api/v1/crawls/?limit=4
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "website_id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "COMPLETED",
      "crawl_depth": 3,
      "max_pages": 50,
      "respect_robots": true,
      "started_at": "2026-05-08T12:00:00Z",
      "completed_at": "2026-05-08T12:05:00Z",
      "pages_discovered": 47,
      "pages_crawled": 47,
      "error_message": null,
      "created_at": "2026-05-08T12:00:00Z",
      "updated_at": "2026-05-08T12:05:00Z"
    }
  ],
  "total": 1
}
```

**Mapping mock → real:**
- `mockCrawl.id` → `crawl_run.id` (UUID string)
- `mockCrawl.website` → **NOT AVAILABLE** in this response — need `GET /api/v1/websites/{website_id}` separately
- `mockCrawl.status` → `crawl_run.status` (lowercase string: `"completed"`)
- `mockCrawl.pages` → `crawl_run.pages_crawled`
- `mockCrawl.date` → computed from `crawl_run.created_at` (format: `"2h ago"`, `"1d ago"`) — frontend must do date arithmetic client-side