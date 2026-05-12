# RYZEN9_DASHBOARD_API_002_WIRING

## Task Summary

MTVSEO-DASHBOARD-API-002: Wire Websites, Crawl Runs, and SEO Issues panels to the dashboard.

## Branch Context

- **Base branch:** `feature/backend-phase2`
- **Base commit:** `1fb76fb merge: integrate businesses dashboard API wiring`
- **Feature branch:** `feature/dashboard-api-002-websites-crawls-issues`
- **Created from:** `1fb76fb`
- **Previous slice:** `feature/ryzen9-api-wiring-businesses-next` (merged into `feature/backend-phase2` at `1fb76fb`)

## Endpoint Contracts Used

### Websites (aligned with `services/api/routers/websites.py`)

List: `GET /api/v1/websites/`
Response: `{ items: Website[], total: number }`

**Website fields used:**
```typescript
interface Website {
  id: string;         // UUID string
  business_id: string; // UUID string
  url: string;
  name: string | null;
  created_at: string;  // ISO datetime
  updated_at: string;   // ISO datetime
}
```

### Crawl Runs (existing wiring — verified correct)

Files already existed at `apps/web/src/lib/api/types/crawls.ts` and `apps/web/src/lib/queries/useCrawls.ts`.
Verified correct against `services/api/schemas/crawl_run.py` — no changes needed.

### SEO Issues (NOT YET BACKEND-ROUTED — wire only, will not return data until backend router is added)

List: `GET /api/v1/seo-issues/` (endpoint exists in model, no router yet)
Response: `{ items: SeoIssue[], total: number }`

**SeoIssue fields used:**
```typescript
interface SeoIssue {
  id: string;
  page_id: string | null;   // nullable
  crawl_run_id: string;
  issue_type: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
  title: string;
  description: string | null;
  recommendation: string | null;
  affected_element: string | null;
  created_at: string;
  updated_at: string;
}
```

**NOTE:** There is no backend router for SEO issues yet. The model `SeoIssue` exists (`services/api/models/seo_issue.py`), but no `seo_issues` router has been included in `main.py`. The frontend query hook and type are wired now so the dashboard panel will render when the backend router is added. Until then, the panel will show the empty state.

## Files Added

### Types

- `apps/web/src/lib/api/types/websites.ts` — `Website`, `WebsiteListResponse`
- `apps/web/src/lib/api/types/seo_issues.ts` — `SeoIssue`, `SeoIssueListResponse`, `SEVERITY_LABELS`, `SEVERITY_VARIANTS`

### Query Hooks

- `apps/web/src/lib/queries/useWebsites.ts` — `useWebsites()`
- `apps/web/src/lib/queries/useSeoIssues.ts` — `useSeoIssues()`

### Routes

- `apps/web/src/lib/api/routes.ts` — added `SEO_ISSUES` and `SEO_ISSUE_BY_ID` entries

### Dashboard Page

- `apps/web/src/app/page.tsx` — added Websites panel, replaced Top Issues (mock) with SEO Issues (API-wired) panel, wired useWebsites and useSeoIssues hooks

## Dashboard Panels Added

### Websites
- Icon: Globe (purple)
- Shows: site name or URL, URL, business_id prefix
- States: loading, error, empty, populated
- Max 4 rows, sorted by created_at desc

### SEO Issues (replaces Top Issues mock data)
- Shows: issue title, issue_type, page_id prefix, severity badge
- States: loading, error, empty, populated
- Uses real severity labels: Critical, High, Medium, Low, Info
- Max 4 rows, sorted by created_at desc

## Behavior Notes

- All panels handle null/missing fields gracefully
- No hardcoded API URLs — uses `API_ROUTES` constants
- No fake live data — API-powered only with empty-state fallback
- The `topIssues` mock array was removed from page.tsx
- The mock crawls (`MOCK_CRAWLS`) were removed; Recent Crawls shows real API rows only, with empty state when API returns 0 items

## Frontend Type Alignment

| Backend field | Frontend type | Notes |
|---|---|---|
| `WebsiteRead.id` | `string` | UUID as string |
| `WebsiteRead.business_id` | `string` | UUID as string |
| `WebsiteRead.url` | `string` | |
| `WebsiteRead.name` | `string \| null` | nullable |
| `WebsiteRead.created_at` | `string` | ISO datetime |
| `SeoIssue.page_id` | `string \| null` | nullable per model |
| `SeoIssue.severity` | `IssueSeverity` | enum: CRITICAL/HIGH/MEDIUM/LOW/INFO |
| `SeoIssue.title` | `string` | mapped from `recommendation` field in task doc, but actual model has `title` field |

## Known Limitations

1. **SEO Issues backend router missing** — The `SeoIssue` model exists but no router has been added to `main.py`. The frontend hook will return an empty list (404 from undefined endpoint) or error state until a router is added. This is intentional — we wire now, backend adds router later.

2. **No website name join** — The crawl runs panel shows `website_id` prefix only (no website name). The `CrawlRunRead` schema does not include a joined website name. A future backend enhancement could add this.

3. **No score column** — `CrawlRunRead` has no score field. The dashboard shows `—` as a placeholder.

4. **No auth** — All queries are unauthenticated. Auth wiring is out of scope.

## Verification Commands Run

```bash
git status
git diff --cached --stat
```

Full verification bundle (from repo root):
```bash
.venv/bin/python scripts/verify_local.py
.venv/bin/python -m pytest tests/ -q --tb=no
.venv/bin/python -m compileall services packages tests
cd apps/web && npm install && npm run build && cd ../..
```

## Next Recommended Slice

1. Add `seo_issues` router to `main.py` and `routers/__init__.py`
2. Wire a `/seo-issues` dedicated page if low-risk
3. Add website name to crawl runs panel (backend join or separate query)
4. Add POST/DELETE endpoints for Websites and Crawls when CRUD is needed