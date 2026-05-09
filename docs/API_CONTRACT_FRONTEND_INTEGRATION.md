# API Contract for Frontend Integration

## Context

- **Base branch:** `feature/backend-phase2`
- **Base commit:** `f30bb33` ("Merge AgentTask foreign key constraints")
- **Purpose:** Document the stable REST API route contracts for future frontend integration. This is a read-only reference document. No backend implementation changes are made in this branch.
- **Scope:** All `/api/v1/` REST routes for businesses, websites, crawls, and pages.
- **Frontend audience:** Agents wiring the Step Flash dashboard mock UI, and any future React/Vue/Svelte frontend consuming this API.

---

## Current REST Route Map

All routes are under the `/api/v1/` prefix. Routes use REST entity-prefixed paths (e.g., `/api/v1/businesses/`, not ambiguous `/api/v1/`).

```
GET,HEAD  /docs              — Swagger UI (OAuth2 redirect)
GET,HEAD  /docs/oauth2-redirect  — OAuth2 redirect
GET       /health            — Health check
GET,HEAD  /openapi.json      — OpenAPI spec
GET,HEAD  /redoc             — ReDoc

GET       /api/v1/businesses/                        list_businesses
POST      /api/v1/businesses/                        create_business
GET       /api/v1/businesses/{business_id}           get_business
PATCH     /api/v1/businesses/{business_id}           update_business
DELETE    /api/v1/businesses/{business_id}           delete_business

GET       /api/v1/websites/                         list_websites
POST      /api/v1/websites/                         create_website
GET       /api/v1/websites/{website_id}             get_website
PATCH     /api/v1/websites/{website_id}             update_website
DELETE    /api/v1/websites/{website_id}             delete_website

GET       /api/v1/crawls/                           list_crawl_runs
POST      /api/v1/crawls/                           trigger_crawl
GET       /api/v1/crawls/{crawl_run_id}              get_crawl_run
POST      /api/v1/crawls/{crawl_run_id}/cancel      cancel_crawl_run
GET       /api/v1/crawls/{crawl_run_id}/status      get_crawl_run_status

GET       /api/v1/pages/                             list_pages
GET       /api/v1/pages/by-url/                      get_page_by_url
GET       /api/v1/pages/summary/{page_id}            get_page_summary
GET       /api/v1/pages/{page_id}                     get_page
```

---

## Business Endpoints

### `POST /api/v1/businesses/`

**Purpose:** Create a new business record.

**Request body:**
```json
{
  "name": "string (required, 1-255 chars)",
  "website_url": "string | null (max 500)",
  "description": "string | null",
  "business_type": "string | null (max 100)",
  "location": "string | null (max 500)",
  "phone": "string | null (max 50)",
  "email": "string | null (valid email format)",
  "is_cannabis": "boolean (default false)",
  "is_ymyl": "boolean (default false)"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "string",
  "website_url": "string | null",
  "description": "string | null",
  "business_type": "string | null",
  "location": "string | null",
  "phone": "string | null",
  "email": "string | null",
  "is_cannabis": false,
  "is_ymyl": false,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error behavior:** 422 for validation errors (missing required `name`, invalid email format). 401/403 if not authenticated.

**Related tests:** `test_create_business` (`tests/test_endpoint_crud.py`)

---

### `GET /api/v1/businesses/`

**Purpose:** List all businesses accessible to the current user.

**Query parameters:** None (pagination not implemented in current router — returns full list).

**Response (200 OK):**
```json
{
  "items": [...BusinessRead objects...],
  "total": "integer"
}
```

**Related tests:** `test_list_businesses` (`tests/test_endpoint_crud.py`)

---

### `GET /api/v1/businesses/{business_id}`

**Purpose:** Get a single business by UUID.

**Path parameter:** `business_id` (UUID)

**Response (200 OK):** Full `BusinessRead` object.

**Error behavior:** 404 if not found.

**Related tests:** `test_get_business_by_id` (`tests/test_endpoint_crud.py`)

---

### `PATCH /api/v1/businesses/{business_id}`

**Purpose:** Update one or more fields on a business.

**Path parameter:** `business_id` (UUID)

**Request body:** Partial `BusinessUpdate` — all fields optional:
```json
{
  "name": "string | null",
  "website_url": "string | null",
  "description": "string | null",
  "business_type": "string | null",
  "location": "string | null",
  "phone": "string | null",
  "email": "string | null",
  "is_cannabis": "boolean | null",
  "is_ymyl": "boolean | null"
}
```

**Response (200 OK):** Updated `BusinessRead` object.

**Error behavior:** 404 if not found. 422 for validation errors.

**Related tests:** `test_update_business` (`tests/test_endpoint_crud.py`)

---

### `DELETE /api/v1/businesses/{business_id}`

**Purpose:** Delete a business and cascade-delete owned websites, crawl_runs, pages, etc.

**Path parameter:** `business_id` (UUID)

**Response (204 No Content):** Empty body on success.

**Error behavior:** 404 if not found.

**Related tests:** `test_delete_business` (`tests/test_endpoint_crud.py`)

---

## Website Endpoints

### `POST /api/v1/websites/`

**Purpose:** Register a new website under a business.

**Request body:**
```json
{
  "business_id": "uuid (required)",
  "url": "string (required, 1-500 chars)",
  "name": "string | null (max 255)"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "business_id": "uuid",
  "url": "string",
  "name": "string | null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error behavior:** 422 for validation errors. 404 if the referenced `business_id` does not exist (route found, FK constraint enforced at DB layer).

**Related tests:** `test_create_website` (`tests/test_endpoint_crud.py`)

---

### `GET /api/v1/websites/`

**Purpose:** List all websites accessible to the current user.

**Response (200 OK):**
```json
{
  "items": [...WebsiteRead objects...],
  "total": "integer"
}
```

**Related tests:** `test_list_websites` (`tests/test_endpoint_crud.py`)

---

### `GET /api/v1/websites/{website_id}`

**Purpose:** Get a single website by UUID.

**Path parameter:** `website_id` (UUID)

**Response (200 OK):** Full `WebsiteRead` object.

**Error behavior:** 404 if not found.

**Related tests:** `test_get_website_by_id` (`tests/test_endpoint_crud.py`)

---

### `PATCH /api/v1/websites/{website_id}`

**Purpose:** Update website URL or name.

**Path parameter:** `website_id` (UUID)

**Request body:**
```json
{
  "url": "string | null (min_length=1, max_length=500)",
  "name": "string | null (max_length=255)"
}
```

**Response (200 OK):** Updated `WebsiteRead` object.

**Error behavior:** 404 if not found.

**Related tests:** `test_update_website` (`tests/test_endpoint_crud.py`)

---

### `DELETE /api/v1/websites/{website_id}`

**Purpose:** Delete a website and cascade-delete owned crawl_runs, pages, etc.

**Path parameter:** `website_id` (UUID)

**Response (204 No Content):** Empty body on success.

**Error behavior:** 404 if not found.

**Related tests:** `test_delete_website` (`tests/test_endpoint_crud.py`)

---

## Crawl Endpoints

### `POST /api/v1/crawls/`

**Purpose:** Trigger a new crawl run for a website.

**Request body:**
```json
{
  "website_id": "uuid (required)",
  "crawl_depth": "integer (default 3, range 1-10)",
  "max_pages": "integer (default 50, range 1-500)",
  "respect_robots": "boolean (default true)"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "website_id": "uuid",
  "crawl_depth": 3,
  "max_pages": 50,
  "respect_robots": true,
  "status": "PENDING",
  "started_at": null,
  "completed_at": null,
  "pages_discovered": 0,
  "pages_crawled": 0,
  "error_message": null,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error behavior:** 422 for validation errors. 404 if `website_id` does not exist.

**Related tests:** `test_trigger_crawl` (`tests/test_endpoint_crud.py`)

---

### `GET /api/v1/crawls/`

**Purpose:** List all crawl runs accessible to the current user.

**Response (200 OK):**
```json
{
  "items": [...CrawlRunRead objects...],
  "total": "integer"
}
```

**Related tests:** `test_list_crawl_runs` (`tests/test_endpoint_crud.py`)

---

### `GET /api/v1/crawls/{crawl_run_id}`

**Purpose:** Get full details of a crawl run.

**Path parameter:** `crawl_run_id` (UUID)

**Response (200 OK):** Full `CrawlRunRead` object.

**Error behavior:** 404 if not found.

**Related tests:** `test_get_crawl_run` (`tests/test_endpoint_crud.py`)

---

### `POST /api/v1/crawls/{crawl_run_id}/cancel`

**Purpose:** Cancel a running or pending crawl run.

**Path parameter:** `crawl_run_id` (UUID)

**Request body:** None (empty)

**Response (200 OK):** Updated `CrawlRunRead` object with `status` set to `CANCELLED`.

**Error behavior:** 404 if not found. 409 if crawl is not in CANCELLABLE state.

**Related tests:** `test_cancel_crawl_run` (`tests/test_endpoint_crud.py`)

---

### `GET /api/v1/crawls/{crawl_run_id}/status`

**Purpose:** Lightweight status check for a crawl run (for polling).

**Path parameter:** `crawl_run_id` (UUID)

**Response (200 OK):**
```json
{
  "id": "uuid",
  "status": "PENDING|RUNNING|COMPLETED|FAILED|CANCELLED",
  "pages_discovered": "integer",
  "pages_crawled": "integer",
  "error_message": "string | null"
}
```

**Error behavior:** 404 if not found.

---

## Page Endpoints

### `GET /api/v1/pages/`

**Purpose:** List pages, optionally filtered by crawl_run_id.

**Query parameters:** `crawl_run_id` (optional UUID query param for filtering).

**Response (200 OK):**
```json
{
  "items": [...PageRead objects...],
  "total": "integer",
  "page": 1,
  "page_size": 50
}
```

**Related tests:** `test_list_pages` (`tests/test_endpoint_crud.py`)

---

### `GET /api/v1/pages/{page_id}`

**Purpose:** Get a single page by UUID.

**Path parameter:** `page_id` (UUID)

**Response (200 OK):** Full `PageRead` object.

**Error behavior:** 404 if not found.

**Related tests:** `test_get_page_by_id` (`tests/test_endpoint_crud.py`)

---

### `GET /api/v1/pages/summary/{page_id}`

**Purpose:** Lightweight page summary for list-view optimization.

**Path parameter:** `page_id` (UUID)

**Response (200 OK):**
```json
{
  "id": "uuid",
  "url": "string",
  "status_code": "integer | null",
  "title": "string | null",
  "has_schema": "boolean",
  "is_indexable": "boolean",
  "word_count": "integer | null"
}
```

---

### `GET /api/v1/pages/by-url/`

**Purpose:** Look up a page by exact URL string.

**Query parameters:** `url` (required, URL-encoded string).

**Response (200 OK):** Full `PageRead` object.

**Error behavior:** 404 if no page with that URL exists in the DB.

---

## Shared Schema Reference

### BusinessRead
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "string",
  "website_url": "string | null",
  "description": "string | null",
  "business_type": "string | null",
  "location": "string | null",
  "phone": "string | null",
  "email": "string | null",
  "is_cannabis": "boolean",
  "is_ymyl": "boolean",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### WebsiteRead
```json
{
  "id": "uuid",
  "business_id": "uuid",
  "url": "string",
  "name": "string | null",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### CrawlRunRead
```json
{
  "id": "uuid",
  "website_id": "uuid",
  "status": "PENDING|RUNNING|COMPLETED|FAILED|CANCELLED",
  "crawl_depth": "integer",
  "max_pages": "integer",
  "respect_robots": "boolean",
  "started_at": "datetime | null (ISO 8601)",
  "completed_at": "datetime | null (ISO 8601)",
  "pages_discovered": "integer",
  "pages_crawled": "integer",
  "error_message": "string | null",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### PageRead
```json
{
  "id": "uuid",
  "crawl_run_id": "uuid",
  "url": "string (max 2000)",
  "canonical_url": "string | null",
  "status_code": "integer | null",
  "title": "string | null",
  "meta_description": "string | null",
  "h1": "string | null",
  "h2_headings": "list | null",
  "word_count": "integer | null",
  "internal_links_count": "integer",
  "external_links_count": "integer",
  "images_count": "integer",
  "images_without_alt": "integer",
  "has_schema": "boolean",
  "schema_types": "list | null",
  "is_indexable": "boolean",
  "is_canonical": "boolean",
  "is_robots_blocked": "boolean",
  "crawl_depth": "integer | null",
  "parent_page_id": "uuid | null",
  "redirect_url": "string | null",
  "created_at": "datetime (ISO 8601)"
}
```

---

## UUID Handling

**Frontend developers must treat all IDs as strings and preserve canonical UUID format.**

- All primary keys and foreign keys are `UUID` (36-char hyphenated string, e.g., `"12345678-1234-5678-1234-567812345678"`)
- Frontend should never parse or transform UUIDs — pass them as raw strings to API calls
- In JSON request bodies, serialize UUIDs as strings
- In URL path parameters, UUIDs are case-sensitive
- SQLite test DB may store UUIDs as hex without hyphens in raw SQL queries, but the API always returns hyphenated canonical form — frontend should always send/receive hyphenated UUID strings

---

## Frontend Integration Notes

### Recommended API client structure

```typescript
// Base client — all requests include Authorization header
// API_BASE = process.env.VITE_API_BASE_URL || '/api/v1'

// Businesses
GET    /api/v1/businesses/
POST   /api/v1/businesses/
GET    /api/v1/businesses/:business_id
PATCH  /api/v1/businesses/:business_id
DELETE /api/v1/businesses/:business_id

// Websites
GET    /api/v1/websites/
POST   /api/v1/websites/
GET    /api/v1/websites/:website_id
PATCH  /api/v1/websites/:website_id
DELETE /api/v1/websites/:website_id

// Crawls
GET    /api/v1/crawls/
POST   /api/v1/crawls/
GET    /api/v1/crawls/:crawl_run_id
POST   /api/v1/crawls/:crawl_run_id/cancel
GET    /api/v1/crawls/:crawl_run_id/status

// Pages
GET    /api/v1/pages/
GET    /api/v1/pages/:page_id
GET    /api/v1/pages/summary/:page_id
GET    /api/v1/pages/by-url/?url=<encoded-url>
```

### React Query keys (recommended)

```typescript
// Business keys
['businesses', 'list']
['businesses', 'detail', businessId]

// Website keys
['websites', 'list']
['websites', 'list', { businessId }]
['websites', 'detail', websiteId]

// Crawl keys
['crawls', 'list']
['crawls', 'list', { websiteId }]
['crawls', 'detail', crawlRunId]
['crawls', 'status', crawlRunId]

// Page keys
['pages', 'list']
['pages', 'list', { crawlRunId }]
['pages', 'detail', pageId]
['pages', 'summary', pageId]
['pages', 'by-url', url]
```

### Loading / Error / Empty state expectations

- All list endpoints return `items: T[]` and `total: number` — use `total === 0` for empty state, not a separate `items.length === 0` check
- All single-resource endpoints return the resource object directly
- 404 responses should show "not found" UI state, not an error toast
- 422 responses include Pydantic validation detail — display field-level errors inline
- 401/403 should redirect to login or show permission denied UI

### Do NOT use legacy ambiguous routes

`POST /api/v1/` (without entity prefix) is NOT a valid route — it was the root cause of the routing collision bug fixed in the Ryzen 9 CRUD work. Frontend must always use the entity-prefixed paths.

---

## Known Deferred Backend Items

### Auth / User Ownership

Auth/user ownership is not fully productized in the current backend. The `user_id` on `Business` and the `created_by` fields on several models exist but:
- No documented JWT/session authentication middleware is currently wired for all endpoints
- `MockUser` override is used in test fixtures — production auth behavior is not confirmed for all routes
- Frontend should NOT assume any particular auth/session behavior until the auth middleware is documented

### ContentBrief.website Relationship Asymmetry

`ContentBrief.website` uses a bare `relationship("Website")` without `back_populates` on the `Website` model. This is a deferred ORM hygiene fix. No API contract impact — the relationship works, it's just asymmetric.

### AgentTask FK Migration — Orphan Data Check

The `20260508_0001_add_agent_task_business_website_fk.py` migration can fail in production if there are `agent_tasks` rows with invalid (non-existent) `business_id` or `website_id` values. The migration does not clean up orphaned rows — it surfaces them as failures. This affects future use of `AgentTask` endpoints, which are not yet implemented.

### Crawl Run Status Polling

The crawl run model uses async background task execution (Celery/Redis mentioned in dependencies) but the current implementation may not have full async status propagation. Frontend should poll `GET /api/v1/crawls/{crawl_run_id}/status` at reasonable intervals (e.g., 5-10s) rather than relying on webhooks/subscriptions.

---

## Verification Results

```
python scripts/verify_local.py               ✓ ALL CHECKS PASSED
pytest tests/                                 ✓ 34 passed (0 failed)
python -m compileall services packages tests  ✓ no errors
```

---

## Recommended Next Step

**Frontend API wiring should begin only after the Step Flash mock UI branch (`origin/feature/stepflash-dashboard-shell-mock-ui`) is merged into `feature/backend-phase2`.**

This ensures:
1. The mock UI has confirmed the expected data shapes and routing structure
2. Any schema mismatches between mock UI expectations and actual API contracts are surfaced before real integration work begins
3. The frontend integration contract in this document has been reviewed by the Step Flash agent

Until then, frontend agents should treat this document as authoritative reference and use the `/docs` OpenAPI endpoint for interactive schema exploration.

---

## Appendix: All Route Summary Table

| Method | Path | Handler | Notes |
|--------|------|---------|-------|
| POST | `/api/v1/businesses/` | create_business | Returns 201 + BusinessRead |
| GET | `/api/v1/businesses/` | list_businesses | Returns BusinessList |
| GET | `/api/v1/businesses/{business_id}` | get_business | Returns BusinessRead |
| PATCH | `/api/v1/businesses/{business_id}` | update_business | Returns BusinessRead |
| DELETE | `/api/v1/businesses/{business_id}` | delete_business | Returns 204 |
| POST | `/api/v1/websites/` | create_website | Returns 201 + WebsiteRead |
| GET | `/api/v1/websites/` | list_websites | Returns WebsiteList |
| GET | `/api/v1/websites/{website_id}` | get_website | Returns WebsiteRead |
| PATCH | `/api/v1/websites/{website_id}` | update_website | Returns WebsiteRead |
| DELETE | `/api/v1/websites/{website_id}` | delete_website | Returns 204 |
| POST | `/api/v1/crawls/` | trigger_crawl | Returns 201 + CrawlRunRead |
| GET | `/api/v1/crawls/` | list_crawl_runs | Returns CrawlRunList |
| GET | `/api/v1/crawls/{crawl_run_id}` | get_crawl_run | Returns CrawlRunRead |
| POST | `/api/v1/crawls/{crawl_run_id}/cancel` | cancel_crawl_run | Returns CrawlRunRead |
| GET | `/api/v1/crawls/{crawl_run_id}/status` | get_crawl_run_status | Returns CrawlRunStatus |
| GET | `/api/v1/pages/` | list_pages | Returns PageList |
| GET | `/api/v1/pages/{page_id}` | get_page | Returns PageRead |
| GET | `/api/v1/pages/summary/{page_id}` | get_page_summary | Returns PageSummary |
| GET | `/api/v1/pages/by-url/` | get_page_by_url | Returns PageRead |