# Ryzen 9 SEO Issues Router 001

## Branch
`feature/seo-issues-router-001`

## Base
`feature/backend-phase2` (commit `08db133`)

## Goal
Implement real backend SEO Issues route so the already-wired frontend SEO Issues panel can fetch database-backed SEO issue records instead of showing a route-missing error.

## API Routes

### `GET /api/v1/seo-issues/`
List all SEO issues, optionally filtered.

**Query parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page_id` | UUID (optional) | — | Filter by page |
| `crawl_run_id` | UUID (optional) | — | Filter by crawl run |
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 20 (max 100) | Page size |

**Response `200`:**
```json
{
  "items": [
    {
      "id": "uuid",
      "page_id": "uuid | null",
      "crawl_run_id": "uuid",
      "issue_type": "string",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "string",
      "description": "string | null",
      "recommendation": "string | null",
      "affected_element": "string | null",
      "created_at": "ISO8601 datetime",
      "updated_at": "ISO8601 datetime"
    }
  ],
  "total": 0
}
```

### `GET /api/v1/seo-issues/{seo_issue_id}`
Get a single SEO issue by ID.

**Response `200`:** Single `SeoIssueRead` object (same shape as list item above).
**Response `404`:** `{"detail": "SeoIssue with id=... not found"}`

## Files Changed

| File | Change |
|------|--------|
| `services/api/schemas/seo_issue.py` | New — `SeoIssueRead` and `SeoIssueList` Pydantic schemas |
| `services/api/routers/seo_issues.py` | New — `GET /seo-issues/` and `GET /seo-issues/{id}` endpoints |
| `services/api/main.py` | Import and register `seo_issues` router |
| `tests/test_router_imports.py` | Add `test_seo_issues_router_import` |
| `tests/test_endpoint_smoke.py` | Add `/api/v1/seo-issues/` to mount check paths |
| `tests/test_endpoint_crud.py` | Add 5 new SEO issues tests |

## Tests Added

- `test_seo_issues_router_import` — router imports cleanly
- `test_list_seo_issues_empty` — empty DB returns `{"items": [], "total": 0}`
- `test_list_seo_issues_returns_seeded_records` — seeded record appears in list
- `test_list_seo_issues_filtered_by_crawl_run` — `?crawl_run_id=` filter works; unrelated ID returns empty
- `test_get_seo_issue_by_id` — returns correct record with all fields
- `test_get_seo_issue_not_found` — returns 404 for nonexistent ID

## Verification Results

| Check | Result |
|-------|--------|
| `verify_local.py` | ✓ ALL CHECKS PASSED |
| `pytest tests/ -q` | ✓ 40 passed in 2.67s |
| `python -m compileall` | ✓ No errors |
| `npm install` | ✓ Success |
| `npm run build` | ✓ Compiled successfully |
| Mock/fake source check | ✓ No fake user-facing SEO issue data in active source |

## Response Contract Alignment
- Frontend `SeoIssue` TypeScript type has `severity: IssueSeverity` where `IssueSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO"` — matches backend `IssueSeverity` enum values exactly.
- Backend `SeoIssueRead` uses `severity: str` (Pydantic serializes enum to string value automatically).
- `page_id` is nullable in both frontend type and backend model.

## Known Limitations
- No `POST /api/v1/seo-issues/` — SEO issues are created by the crawl process, not directly via API.
- No pagination beyond `skip`/`limit` (cursor-based not implemented).
- No filter by `severity` or `issue_type` on list endpoint.
- Frontend dashboard still has pre-existing hardcoded mock data for `metrics` and `keywordOpportunities` arrays (unrelated to SEO Issues panel).
