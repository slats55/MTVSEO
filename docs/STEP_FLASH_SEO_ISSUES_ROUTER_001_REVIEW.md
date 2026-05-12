# Step Flash SEO Issues Router 001 Review

## Branch Reviewed
`feature/seo-issues-router-001`

## Base Branch
`feature/backend-phase2`

## Reviewed Commit
`6be111aa1233eb166f19ec94410a108ebd68f994` ("feat(api): add SEO issues router")

## Files Reviewed

| File | Review |
|------|--------|
| `services/api/routers/seo_issues.py` | ✓ New router with `GET /seo-issues/` and `GET /seo-issues/{id}` |
| `services/api/schemas/seo_issue.py` | ✓ `SeoIssueRead` and `SeoIssueList` schemas |
| `services/api/main.py` | ✓ Router imported and registered at `api_v1_prefix` |
| `services/api/models/seo_issue.py` | ✓ Pre-existing model — verified FK constraints present |
| `tests/test_router_imports.py` | ✓ Import test added |
| `tests/test_endpoint_smoke.py` | ✓ Mount check updated |
| `tests/test_endpoint_crud.py` | ✓ 5 new SEO issues tests added |
| `docs/RYZEN9_SEO_ISSUES_ROUTER_001.md` | ✓ Implementation doc created |

## API Contract Verification

### Route Path
- Backend: `GET /api/v1/seo-issues/` (registered via `include_router(seo_issues.router, prefix=api_prefix)`)
- Frontend: `API_ROUTES.SEO_ISSUES = "/api/v1/seo-issues/"` → `${API_ROUTES.SEO_ISSUES}?limit=4&skip=0`
- **Match: ✓**

### Response Shape
Frontend `SeoIssueListResponse`:
```ts
{ items: SeoIssue[]; total: number }
```
Backend `SeoIssueList`:
```python
class SeoIssueList(BaseModel):
    items: list[SeoIssueRead]
    total: int
```
**Match: ✓**

### Field Alignment
| Field | Backend Schema | Frontend Type | Status |
|-------|---------------|---------------|--------|
| `id` | `UUID` | `string` | ✓ (Pydantic serializes) |
| `page_id` | `UUID \| None` | `string \| null` | ✓ |
| `crawl_run_id` | `UUID` | `string` | ✓ |
| `issue_type` | `str` | `string` | ✓ |
| `severity` | `str` (enum value) | `IssueSeverity` union | ✓ |
| `title` | `str` | `string` | ✓ |
| `description` | `str \| None` | `string \| null` | ✓ |
| `recommendation` | `str \| None` | `string \| null` | ✓ |
| `affected_element` | `str \| None` | `string \| null` | ✓ |
| `created_at` | `datetime` | `string` | ✓ (ISO8601) |
| `updated_at` | `datetime` | `string` | ✓ (ISO8601) |

### Query Parameters
Frontend: `?limit=4&skip=0`
Backend: `skip: int = Query(0, ge=0)`, `limit: int = Query(20, ge=1, le=100)`
**Match: ✓**

### GET by ID
- Frontend uses only list endpoint (dashboard query).
- GET by ID exists in backend as `/api/v1/seo-issues/{id}` — correctly returns 404 for missing records.
**Status: ✓**

## Router Registration Verification
- Router imported in `main.py`: `from services.api.routers import ... seo_issues`
- Registered: `app.include_router(seo_issues.router, prefix=api_prefix, tags=["seo-issues"])`
- `api_prefix = settings.api_v1_prefix` → `/api/v1`
- Final paths: `/api/v1/seo-issues/` and `/api/v1/seo-issues/{id}`
**Registration: ✓**

## Database Verification
- `SeoIssue` model has proper FK constraints: `page_id → pages.id` and `crawl_run_id → crawl_runs.id`
- Both FKs have `ondelete="CASCADE"`
- No fake/mock SEO issue data introduced in models, routers, or schemas
**Status: ✓**

## Empty DB Behavior
- `test_list_seo_issues_empty`: returns `{"items": [], "total": 0}` with 200
- Frontend dashboard correctly shows "No SEO issues found." on empty items
**Verified: ✓**

## Seeded DB Behavior
- `test_list_seo_issues_returns_seeded_records`: seeded record appears in list with correct fields
- `test_list_seo_issues_filtered_by_crawl_run`: filter by `crawl_run_id` works
- `test_get_seo_issue_by_id`: returns correct record; 404 for nonexistent ID
**Verified: ✓**

## Mock/Fake Data Check
```
grep -R "MOCK_CRAWLS" apps/web/src services/api/app tests  → Not found
grep -R "mock SEO" apps/web/src services/api/app tests     → Not found
grep -R "fake SEO" apps/web/src services/api/app tests     → Not found
```
**No user-facing mock or fake SEO issue data: ✓**

## Verification Results

| Check | Result |
|-------|--------|
| `python scripts/verify_local.py` | ✓ ALL CHECKS PASSED |
| `pytest tests/ -q` | ✓ 40 passed in 2.16s |
| `python -m compileall` | ✓ No errors |
| `npm install` (apps/web) | ✓ Success |
| `npm run build` (apps/web) | ✓ Compiled successfully |
| Mock/fake source check | ✓ No fake user-facing SEO data |
| Router reachable at `/api/v1/seo-issues/` | ✓ |
| Empty DB returns valid empty response | ✓ |
| Seeded DB returns real records | ✓ |

## Blocking Issues
**None.**

## Non-Blocking Issues

1. **Minor schema inconsistency**: `SeoIssueRead.page_id` is typed as `UUID | None` but `SeoIssue.page_id` model column has `nullable=False`. This is cosmetic in practice — Pydantic's `from_attributes=True` will accept a non-null UUID from the ORM. No runtime bug observed. The frontend already handles `page_id | null` correctly. *Recommended fix: change schema to `page_id: UUID` to match model, but not a blocker.*

2. **Pre-existing mock data in dashboard**: `page.tsx` still has hardcoded `metrics[]` and `keywordOpportunities[]` arrays — these are unrelated to the SEO Issues panel and were present before this branch. Not a regression.

3. **Documentation note in RYZEN9_SEO_ISSUES_ROUTER_001.md** states "`page_id` is nullable in both frontend type and backend model" — the model is actually NOT nullable (a doc inaccuracy, not a code issue).

## Merge Recommendation

**APPROVED_FOR_MERGE**

### Rationale
- Route is correctly implemented and registered at `/api/v1/seo-issues/`
- Response contract matches frontend TypeScript types exactly
- All 40 tests pass including 5 new SEO issues tests
- Empty DB returns honest empty response (not sample rows)
- Seeded DB returns real records
- No fake/mock user-facing SEO issue data introduced
- Frontend build succeeds
- Working tree is clean (only unrelated untracked file `docs/homepc-next-feature-plan.md`)
- Implementation follows existing project patterns

The single non-blocking schema note (page_id nullability) does not affect functionality and can be addressed in a follow-up if desired.
