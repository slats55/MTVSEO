# Dashboard Audit Trigger Flow — Planning Document

**Task ID:** MTVSEO-DASHBOARD-AUDIT-FLOW-001  
**Planning Branch:** `docs/homepc-dashboard-audit-flow-plan`  
**Planner:** Home PC (Mr.M7)  
**Date:** 2026-05-11  
**Base Commit:** `18a9504`  
**Status:** PLANNING COMPLETE — Ready for Mr.R9

---

## 1. Context

### Stable Base
- **Branch:** `feature/backend-phase2`
- **Commit:** `18a9504` (merge: integrate SEO issues router)
- **Verified by:** Step Flash — BASE_BRANCH_CONFIRMED_STABLE

### What Exists
1. **Dashboard API 002** — Panels wired to real API (websites, crawls, SEO issues)
2. **SEO Issues Router 001** — `GET /api/v1/seo-issues/` and `GET /api/v1/seo-issues/{id}` verified
3. **CrawlRun model** — `status` enum: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
4. **Existing trigger endpoint:** `POST /api/v1/crawls/` — creates a CrawlRun with status=PENDING
5. **ReportType enum** — SEO_AUDIT, GEO_AUDIT, FULL_AUDIT, CONTENT_AUDIT

### Known Gaps
- No endpoint to trigger a standalone SEO audit (generates issues)
- No endpoint to trigger a standalone GEO audit (generates geo_issues)
- Dashboard "Run SEO Audit" / "Run GEO Audit" buttons are navigation links only (href="/audits")
- Dashboard metric cards show hardcoded values (72, 58, 81, 94)
- No audit/crawl trigger mutation exists in the frontend React Query layer

---

## 2. Goal

Implement the **Dashboard Audit Trigger Flow** so that:

1. Dashboard buttons ("New Crawl", "Run SEO Audit", "Run GEO Audit") call **real backend endpoints**
2. Backend creates **honest pending/running job records** (not fake completed results)
3. UI reflects **real pending/running/error states** from the database
4. **No fake scores**, **no fake SEO issues**, **no fake audit results**

---

## 3. Scope

### ✅ In Scope (Phase 1)
- `POST /api/v1/crawls/` already exists — wire dashboard "New Crawl" to this endpoint
- Create `POST /api/v1/audits/` with `type` field (SEO_AUDIT | GEO_AUDIT) that creates an audit job record
- Create audit job model/table if needed, or reuse existing patterns
- Frontend mutation hook for triggering audits
- Dashboard "Run SEO Audit" / "Run GEO Audit" buttons call the mutation
- UI shows honest pending/running/error state from API response
- Existing crawl list updates after triggering

### ❌ Out of Scope
- Full crawler engine implementation
- Fake completed audit results
- Fake SEO issue generation
- Fake score calculation
- GSC integration
- Broad dashboard redesign
- Replacing the metric cards (non-blocking, separate issue)

---

## 4. Technical Analysis

### 4.1 Existing Patterns to Follow

**Backend API conventions (from `services/api/routers/crawls.py`):**

```python
@router.post("/crawls/", response_model=CrawlRunRead, status_code=status.HTTP_201_CREATED)
async def trigger_crawl(
    data: CrawlRunCreate,
    db: AsyncSession = Depends(get_db),
) -> CrawlRunRead:
    # 1. Validate foreign key (website exists)
    # 2. Create model instance with status=PENDING
    # 3. db.add() + await db.flush()
    # 4. Return created record
```

**Frontend conventions (from `apps/web/src/lib/queries/`):**
- React Query `useMutation` for writes
- `useCrawls()`, `useWebsites()`, `useSeoIssues()` for reads
- API routes in `apps/web/src/lib/api/routes.ts`

### 4.2 Recommended API Routes

**Option A — Reuse crawls endpoint (simplest, recommended for Phase 1):**
- `POST /api/v1/crawls/` — already exists, creates CrawlRun with PENDING status
- Trigger "New Crawl" → calls this directly
- SEO/GEO audits → also call this but set an `audit_type` field on CrawlRun

**Option B — New audits endpoint:**
- `POST /api/v1/audits/` — creates a new `AuditJob` record
- Separate from CrawlRun for clarity

**Decision:** Option A is preferred for Phase 1 because:
- The endpoint already exists and follows all conventions
- It creates real PENDING records
- CrawlRun already has relationships to seo_issues and geo_issues
- Simpler than introducing a new model

### 4.3 Request/Response Contracts

**Existing `POST /api/v1/crawls/`:**

Request:
```json
{
  "website_id": "uuid",
  "crawl_depth": 3,
  "max_pages": 50,
  "respect_robots": true
}
```

Response (201):
```json
{
  "id": "uuid",
  "website_id": "uuid",
  "status": "PENDING",
  "crawl_depth": 3,
  "max_pages": 50,
  "respect_robots": true,
  "pages_discovered": 0,
  "pages_crawled": 0,
  "started_at": null,
  "completed_at": null,
  "error_message": null,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**For SEO/GEO audit, extend CrawlRunCreate to accept `audit_type` (optional):**

```python
class CrawlRunCreate(BaseModel):
    website_id: UUID
    crawl_depth: int = Field(default=3, ge=1, le=10)
    max_pages: int = Field(default=50, ge=1, le=500)
    respect_robots: bool = Field(default=True)
    audit_type: str | None = None  # "SEO_AUDIT" | "GEO_AUDIT" | None
```

---

## 5. Implementation Plan

### Phase 1: Backend (Mr.R9)

1. **Inspect existing patterns**
   - Review `services/api/routers/crawls.py` (already done — endpoint exists)
   - Review `services/api/models/crawl_run.py`
   - Review `services/api/schemas/crawl_run.py`

2. **Extend CrawlRun schema** (optional — only if audit_type is needed)
   - Add `audit_type: str | None = None` to `CrawlRunCreate`

3. **Extend CrawlRun model** (optional)
   - Add `audit_type: Mapped[str | None]` column if tracking audit type separately

4. **Add audit type to router** (if extending)
   - Validate `audit_type` is one of SEO_AUDIT, GEO_AUDIT, None
   - Store on CrawlRun record

5. **Write tests**
   - `POST /crawls/` returns 201 with valid website_id
   - `POST /crawls/` with invalid website_id returns 404
   - `POST /crawls/` with audit_type returns 201 and stores type
   - Existing SEO Issues routes still pass

### Phase 2: Frontend (Mr.R9)

1. **Create mutation hook** — `useTriggerCrawl()` in `apps/web/src/lib/queries/`
2. **Wire "New Crawl" button** — update dashboard quick action
3. **Wire "Run SEO Audit" button** — calls `POST /crawls/` with `audit_type="SEO_AUDIT"`
4. **Wire "Run GEO Audit" button** — calls `POST /crawls/` with `audit_type="GEO_AUDIT"`
5. **Show honest state** — mutation returns `CrawlRunRead` with `status=PENDING`
6. **Update crawl list** — `useCrawls()` invalidates on success

### Phase 3: Verification (Mr.R9 + Step Flash)

1. Run `python scripts/verify_local.py`
2. Run `pytest tests/ -q`
3. Run `python -m compileall services packages tests scripts`
4. Run `cd apps/web && npm install && npm run build`
5. Verify no fake data: `grep -R "fake\|mock\|sample" apps/web/src services/api/app tests`

---

## 6. Files to Change

### Backend
- `services/api/routers/crawls.py` — add audit_type support (optional)
- `services/api/schemas/crawl_run.py` — add audit_type to CrawlRunCreate
- `services/api/models/crawl_run.py` — add audit_type column (optional)
- `tests/test_crawls.py` — add trigger tests

### Frontend
- `apps/web/src/lib/queries/useCrawlTrigger.ts` (new)
- `apps/web/src/app/page.tsx` — wire buttons to mutation

### Documentation
- `docs/RYZEN9_DASHBOARD_AUDIT_TRIGGER_FLOW_001.md` (Mr.R9 creates)

---

## 7. Constraints

1. **No fake data** — everything must come from real API calls
2. **No fake completion** — audits stay PENDING until worker exists
3. **No score generation** — metric cards remain hardcoded (separate issue)
4. **Single implementer** — Mr.R9 only
5. **No force push** — standard push only
6. **Branch from** `feature/backend-phase2` at `18a9504`

---

## 8. Success Criteria

- [ ] `POST /api/v1/crawls/` creates honest PENDING record
- [ ] Frontend "New Crawl" calls the endpoint
- [ ] Frontend "Run SEO Audit" calls the endpoint with audit_type
- [ ] Frontend "Run GEO Audit" calls the endpoint with audit_type
- [ ] UI shows PENDING state from API response
- [ ] No fake scores, fake issues, or fake completed results
- [ ] All existing tests pass
- [ ] Frontend builds successfully

---

## 9. Reference

- **Myles' task message:** MTVSEO-DASHBOARD-AUDIT-FLOW-001-PREP
- **Stable base commit:** 18a9504
- **Mr.R9 feature branch:** `feature/dashboard-audit-trigger-flow-001`
- **Step Flash review branch:** will review `feature/dashboard-audit-trigger-flow-001`
