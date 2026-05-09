# API Contract for Frontend Integration

## Context

- **Base branch:** `feature/backend-phase2`
- **Base commit:** `4f78e73` ("Merge Step Flash mock dashboard UI")
- **Purpose:** Document the stable REST API route contracts for wiring the Step Flash mock dashboard UI to the backend. This contract was created after the mock dashboard was merged so frontend agents can safely replace mock data with real API calls.
- **Frontend audience:** Agents wiring `apps/web/src/app/page.tsx` (and any future React/Vue/Svelte frontend consuming this API).
- **Docs-only:** No backend or frontend implementation files were modified in this branch.

---

## Current REST Route Map

All routes are under the `/api/v1/` prefix. Routes use REST entity-prefixed paths (e.g., `/api/v1/businesses/`, not the deprecated ambiguous `/api/v1/`).

```
GET,HEAD  /docs                          swagger_ui_html
GET,HEAD  /docs/oauth2-redirect           swagger_ui_redirect
GET       /health                         health_check
GET,HEAD  /openapi.json                   openapi
GET,HEAD  /redoc                          redoc_html

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

GET       /api/v1/crawls/                              list_crawl_runs
POST      /api/v1/crawls/                              trigger_crawl
GET       /api/v1/crawls/{crawl_run_id}               get_crawl_run
POST      /api/v1/crawls/{crawl_run_id}/cancel        cancel_crawl_run
GET       /api/v1/crawls/{crawl_run_id}/status       get_crawl_run_status

GET       /api/v1/pages/                                list_pages
GET       /api/v1/pages/{page_id}                      get_page
GET       /api/v1/pages/summary/{page_id}             get_page_summary
GET       /api/v1/pages/by-url/                        get_page_by_url
```

---

## Business Endpoints

### `POST /api/v1/businesses/` — Create business

**Request body:**
```json
{
  "name": "string (required, 1-255 chars)",
  "website_url": "string | null (max 500)",
  "description": "string | null",
  "business_type": "string | null (max 100)",
  "location": "string | null (max 500)",
  "phone": "string | null (max 50)",
  "email": "string | null (valid email)",
  "is_cannabis": false,
  "is_ymyl": false
}
```
**Response (201):** Full `BusinessRead` object including `id`, `user_id`, `created_at`, `updated_at`.
**Errors:** 422 (validation), 401/403 (auth).

### `GET /api/v1/businesses/` — List businesses

**Response (200):**
```json
{ "items": [...BusinessRead], "total": 0 }
```

### `GET /api/v1/businesses/{business_id}` — Get business

**Response (200):** Full `BusinessRead` object. **Errors:** 404.

### `PATCH /api/v1/businesses/{business_id}` — Update business

**Request body:** Partial `BusinessUpdate` — all fields optional.
**Response (200):** Updated `BusinessRead`. **Errors:** 404, 422.

### `DELETE /api/v1/businesses/{business_id}` — Delete business

**Response (204 No Content).** Cascade-deletes owned websites, crawl_runs, pages.
**Errors:** 404.

**Test coverage:** `test_create_business`, `test_list_businesses`, `test_get_business_by_id`, `test_update_business`, `test_delete_business`

---

## Website Endpoints

### `POST /api/v1/websites/` — Register website

**Request body:**
```json
{
  "business_id": "uuid (required)",
  "url": "string (required, 1-500 chars)",
  "name": "string | null (max 255)"
}
```
**Response (201):** Full `WebsiteRead` object.
**Errors:** 422 (validation), 404 (business_id does not exist — route found, FK enforced at DB layer).

### `GET /api/v1/websites/` — List websites

**Response (200):**
```json
{ "items": [...WebsiteRead], "total": 0 }
```

### `GET /api/v1/websites/{website_id}` — Get website

**Response (200):** Full `WebsiteRead`. **Errors:** 404.

### `PATCH /api/v1/websites/{website_id}` — Update website

**Request body:** `{"url": string | null, "name": string | null}`
**Response (200):** Updated `WebsiteRead`. **Errors:** 404.

### `DELETE /api/v1/websites/{website_id}` — Delete website

**Response (204).** Cascade-deletes owned crawl_runs, pages.
**Errors:** 404.

**Test coverage:** `test_create_website`, `test_list_websites`, `test_get_website_by_id`, `test_update_website`, `test_delete_website`

---

## Crawl Endpoints

### `POST /api/v1/crawls/` — Trigger crawl

**Request body:**
```json
{
  "website_id": "uuid (required)",
  "crawl_depth": 3,
  "max_pages": 50,
  "respect_robots": true
}
```
**Response (201):** Full `CrawlRunRead` with `status: "PENDING"`.
**Errors:** 422, 404 (website_id does not exist).

### `GET /api/v1/crawls/` — List crawl runs

**Response (200):**
```json
{ "items": [...CrawlRunRead], "total": 0 }
```

### `GET /api/v1/crawls/{crawl_run_id}` — Get crawl run

**Response (200):** Full `CrawlRunRead`. **Errors:** 404.

### `POST /api/v1/crawls/{crawl_run_id}/cancel` — Cancel crawl

**Request body:** Empty.
**Response (200):** Updated `CrawlRunRead` with `status: "CANCELLED"`. **Errors:** 404, 409 (not in cancellable state).

### `GET /api/v1/crawls/{crawl_run_id}/status` — Poll crawl status

**Response (200):**
```json
{
  "id": "uuid",
  "status": "PENDING|RUNNING|COMPLETED|FAILED|CANCELLED",
  "pages_discovered": 0,
  "pages_crawled": 0,
  "error_message": null
}
```
**Errors:** 404.

**Test coverage:** `test_trigger_crawl`, `test_list_crawl_runs`, `test_get_crawl_run`, `test_cancel_crawl_run`

---

## Page Endpoints

### `GET /api/v1/pages/` — List pages

**Query params:** `crawl_run_id` (optional UUID filter).
**Response (200):**
```json
{ "items": [...PageRead], "total": 0, "page": 1, "page_size": 50 }
```

### `GET /api/v1/pages/{page_id}` — Get page

**Response (200):** Full `PageRead`. **Errors:** 404.

### `GET /api/v1/pages/summary/{page_id}` — Page summary (lightweight)

**Response (200):**
```json
{
  "id": "uuid",
  "url": "string",
  "status_code": 200,
  "title": "string | null",
  "has_schema": false,
  "is_indexable": true,
  "word_count": 42
}
```
**Use for:** KPI card drill-down, page list rows.

### `GET /api/v1/pages/by-url/` — Get page by URL

**Query params:** `url` (required, URL-encoded).
**Response (200):** Full `PageRead`. **Errors:** 404.

**Test coverage:** `test_list_pages`, `test_get_page_by_id`

---

## Shared Schema Reference

### BusinessRead
```json
{
  "id": "uuid", "user_id": "uuid",
  "name": "string", "website_url": "string|null",
  "description": "string|null", "business_type": "string|null",
  "location": "string|null", "phone": "string|null",
  "email": "string|null",
  "is_cannabis": false, "is_ymyl": false,
  "created_at": "datetime", "updated_at": "datetime"
}
```

### WebsiteRead
```json
{
  "id": "uuid", "business_id": "uuid",
  "url": "string", "name": "string|null",
  "created_at": "datetime", "updated_at": "datetime"
}
```

### CrawlRunRead
```json
{
  "id": "uuid", "website_id": "uuid",
  "status": "PENDING|RUNNING|COMPLETED|FAILED|CANCELLED",
  "crawl_depth": 3, "max_pages": 50, "respect_robots": true,
  "started_at": "datetime|null", "completed_at": "datetime|null",
  "pages_discovered": 0, "pages_crawled": 0,
  "error_message": null,
  "created_at": "datetime", "updated_at": "datetime"
}
```

### PageRead
```json
{
  "id": "uuid", "crawl_run_id": "uuid",
  "url": "string (max 2000)",
  "canonical_url": "string|null",
  "status_code": 200, "title": "string|null",
  "meta_description": "string|null", "h1": "string|null",
  "h2_headings": ["string"]|null,
  "word_count": 42, "internal_links_count": 0,
  "external_links_count": 0, "images_count": 0,
  "images_without_alt": 0, "has_schema": false,
  "schema_types": null, "is_indexable": true,
  "is_canonical": true, "is_robots_blocked": false,
  "crawl_depth": null, "parent_page_id": "uuid|null",
  "redirect_url": null, "created_at": "datetime"
}
```

---

## UUID Handling

All IDs are 36-character hyphenated UUID strings (e.g., `"12345678-1234-5678-1234-567812345678"`).

**Frontend rules:**
- Never parse or transform UUIDs — pass as raw strings
- JSON request bodies: serialize UUIDs as strings
- URL path parameters: case-sensitive, exact match
- The API always returns hyphenated canonical form — never hex-only

---

## Frontend Integration Notes

### Recommended file location
`apps/web/src/lib/api/` — a dedicated API client module.

### Recommended React Query key structure
```typescript
// Businesses
['businesses', 'list']
['businesses', 'detail', businessId]

// Websites
['websites', 'list']
['websites', 'list', { businessId }]
['websites', 'detail', websiteId]

// Crawls
['crawls', 'list']
['crawls', 'list', { websiteId }]
['crawls', 'detail', crawlRunId]
['crawls', 'status', crawlRunId]

// Pages
['pages', 'list']
['pages', 'list', { crawlRunId }]
['pages', 'detail', pageId]
['pages', 'summary', pageId]
['pages', 'by-url', encodedUrl]
```

### Loading / Error / Empty states
- **List endpoints** return `{ items: T[], total: number }` — use `total === 0` for empty, not `items.length`
- **Single-resource** endpoints return the resource object directly
- **404** → show "not found" UI state (not error toast)
- **422** → display field-level validation errors inline
- **401/403** → redirect to login or show permission denied

### Do NOT use deprecated ambiguous routes
`POST /api/v1/` (without entity prefix) is not a valid route — it was the root cause of the routing collision bug. Always use entity-prefixed paths.

---

## Mock Dashboard Mapping

The Step Flash mock dashboard (`apps/web/src/app/page.tsx`) has the following sections. Each maps to a backend endpoint:

### 1. Score Cards (4 cards)
| UI Section | Backend Data Source | Notes |
|------------|--------------------|-------|
| Technical SEO | `GET /api/v1/businesses/{id}` + computed aggregate | No aggregate endpoint yet — computed from `pages` data |
| GEO / AI Visibility | Same | Same |
| Content Quality | `GET /api/v1/crawls/` + `GET /api/v1/pages/` | Score derived from `pages` word_count, has_schema, is_indexable |
| Crawl Health | `GET /api/v1/crawls/` | Count COMPLETED vs FAILED crawl runs |

### 2. Quick Actions
| Action | Links to | Backend trigger |
|--------|----------|----------------|
| New Crawl | `/businesses` | Navigate to business detail → trigger crawl via `POST /api/v1/crawls/` |
| Run SEO Audit | `/audits` | Future endpoint — not yet wired |
| Run GEO Audit | `/audits` | Future endpoint — not yet wired |
| Generate Report | `/reports` | Future endpoint — not yet wired |

### 3. Recent Crawls Table
```typescript
// Replace mock `recentCrawls` array with:
const { data: crawlList } = useQuery({
  queryKey: ['crawls', 'list'],
  queryFn: () => GET('/api/v1/crawls/?limit=10'),
})
// Map: crawl.id → crawl_run_id, crawl.website → join with websites,
// crawl.status → crawl_run.status, crawl.pages → crawl_run.pages_crawled
```

### 4. Top Issues Summary
Mock data hardcoded in `page.tsx`. Replace with:
```typescript
// Future: SEO issues endpoint (not yet implemented)
// GET /api/v1/pages/?status_code_min=400  (filterable)
// SEO issue aggregation: count pages with images_without_alt > 0, etc.
// Until SEO issues API exists, this section remains mock or is hidden.
```

**Note:** The `pages` and `crawl_runs` endpoints can power score card computations and the recent crawls table directly. SEO issue aggregation requires an additional future endpoint (`GET /api/v1/seo-issues/`) that is not yet implemented.

---

## Known Deferred Backend Items

1. **Auth/user ownership not fully productized** — no documented JWT/session auth middleware wired on all endpoints. `MockUser` is used in tests. Frontend must not assume specific auth/session behavior until documented.

2. **ContentBrief.website relationship asymmetry** — `ContentBrief.website` uses bare `relationship("Website")` without `back_populates`. Deferred ORM hygiene fix — no API contract impact.

3. **AgentTask FK migration orphan-data risk** — `20260508_0001` migration fails if `agent_tasks` has rows with invalid `business_id`/`website_id`. Migration does not clean up orphans. Affects future `AgentTask` endpoints (not yet wired to frontend).

4. **SEO/GEO audit and reporting endpoints** — `POST /api/v1/audits`, `POST /api/v1/reports` etc. do not exist yet. Quick actions in the mock UI link to `/audits` and `/reports` which are frontend placeholders.

5. **Crawl run async status propagation** — The crawl model uses Celery/Redis for background execution. Current status polling is the correct approach: poll `GET /api/v1/crawls/{id}/status` at 5-10s intervals.

6. **KPI score computation** — No aggregate score endpoints exist. Frontend must compute Technical SEO / GEO / Content Quality scores client-side from raw `PageRead` data, or a future aggregation service endpoint is needed.

---

## Verification Results

```
python scripts/verify_local.py               ✓ ALL CHECKS PASSED
pytest tests/                                 ✓ 34 passed (0 failed)
python -m compileall services packages tests  ✓ no errors
```

---

## Recommended Next Step

**Step Flash should review this contract, then start a small frontend API client branch** (e.g., `feature/stepflash-api-client`) to replace the mock data in `apps/web/src/app/page.tsx` with real API calls using React Query.

Priority wiring order:
1. `GET /api/v1/crawls/` → Recent Crawls table (replace mock array)
2. `GET /api/v1/businesses/` → Business context header
3. `POST /api/v1/crawls/` → New Crawl quick action (trigger)
4. Score card computation from `PageRead` data (future: aggregation endpoint)

The mock `page.tsx` has a comment: `// Mock data — replace with API calls via React Query` — the replacement can be done incrementally using the query key structure documented above.