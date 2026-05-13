# Home PC — Next Feature Slice Plan

**Branch:** `feature/backend-phase2`
**Context:** Dashboard API wiring complete (businesses, websites, crawls, seo_issues panels). Frontend fully wired, SEO issues router missing in backend. Phase 2 nearing completion.

---

## Current State Summary

| Component | Status |
|-----------|--------|
| Backend CRUD (businesses, websites, crawls, pages) | ✅ Complete |
| Frontend API wiring — businesses panel | ✅ Merged |
| Frontend API wiring — websites panel | ✅ Merged |
| Frontend API wiring — crawls panel | ✅ Merged |
| Frontend API wiring — seo_issues panel | ✅ Merged (router missing in backend) |
| SEO Issues backend router | ❌ Missing (model exists, no router added) |
| Audit endpoints (POST /audits/technical, /audits/geo) | ❌ Missing |
| Celery/RQ worker implementation | ❌ Missing |
| React Query full integration (beyond dashboard) | ⏳ Partial |
| Phase 2 completion | ~75% |

---

## Next Feature Slice: SEO Issues Backend Router + Dashboard Audit Flow

### Goal
Complete the SEO Issues data path end-to-end (backend router + frontend page), then wire up the audit trigger flow on the dashboard so "Run SEO Audit" and "Run GEO Audit" buttons are functional.

### Scope

#### 1. SEO Issues Backend Router (High Priority)

**Why first:** Frontend is already wired and rendering empty state. Adding the router unlocks real data with zero frontend changes.

**Files to add/modify:**
- `services/api/routers/seo_issues.py` — new router with:
  - `GET /api/v1/seo-issues/` — list with optional `crawl_run_id` filter, `page`/`page_size` pagination, sorted by severity then created_at
  - `GET /api/v1/seo-issues/{issue_id}` — single issue detail
- `services/api/routers/__init__.py` — register `seo_issues` router
- `services/api/main.py` — include router in app

**Response shape:** Already defined in frontend types (`apps/web/src/lib/api/types/seo_issues.ts`):
```json
{
  "items": [{ "id", "page_id", "crawl_run_id", "issue_type", "severity", "title", "description", "recommendation", "affected_element", "created_at", "updated_at" }],
  "total": 0
}
```

**Verification:**
- `curl http://localhost:8000/api/v1/seo-issues/` returns paginated list
- Frontend dashboard SEO Issues panel shows real data

---

#### 2. Dashboard Audit Trigger Buttons

**"Run SEO Audit" → POST /api/v1/audits/technical**
**"Run GEO Audit" → POST /api/v1/audits/geo**

**Prerequisite:** Audit endpoints must exist first (see step 3).

**Files to modify:**
- `apps/web/src/app/page.tsx` — wire "Run SEO Audit" / "Run GEO Audit" buttons to mutation hooks
- Add `useTriggerSeoAudit.ts` and `useTriggerGeoAudit.ts` hooks in `apps/web/src/lib/queries/`
- Add audit route constants to `apps/web/src/lib/api/routes.ts`

**UX flow:**
1. User clicks "Run SEO Audit" on dashboard
2. Modal or inline form: select website from dropdown (fetch from `useWebsites()`)
3. Confirm → POST to `/api/v1/audits/technical` with `{ website_id }`
4. Show success toast: "SEO Audit queued — results in a few minutes"
5. Refresh crawl/audit status polling optional

---

#### 3. Audit Endpoints (Backend)

**Files to add:**
- `services/api/routers/seo_audits.py` — `POST /api/v1/audits/technical`
- `services/api/routers/geo_audits.py` — `POST /api/v1/audits/geo`
- These trigger the audit CLI commands asynchronously (Celery task or direct call for MVP)

**Request shape:**
```json
{
  "website_id": "uuid",
  "options": {}  // optional future expansion
}
```

**Response shape:**
```json
{
  "audit_id": "uuid",
  "website_id": "uuid",
  "status": "PENDING",
  "started_at": null,
  "completed_at": null
}
```

**MVP approach:** Direct synchronous call to `seo_audit` or `geo_audit` CLI via subprocess for local dev. Celery task wiring deferred to Phase 2 post-stabilization.

---

## Out of Scope for This Slice

- Celery/RQ worker implementation (defer to Phase 2 post-stabilization)
- Full audit results page (defer to next slice after audit trigger is wired)
- GSC/GA4/PageSpeed integrations (Phase 3)
- Authentication (Phase 4+)
- Multi-user auth

---

## Verification Plan

```bash
# Backend
cd /home/mtv/Projects/seo-agent-os
.venv/bin/python scripts/verify_local.py
.venv/bin/python -m pytest tests/ -q --tb=no
curl http://localhost:8000/api/v1/seo-issues/   # should return 200 + JSON

# Frontend
cd apps/web
npm run build
```

---

## Slice Boundaries

**Stop after:**
- SEO Issues router returns real data from DB
- Audit trigger endpoints exist (201 response) even if execution is synchronous
- Dashboard audit buttons are wired to mutations (empty handlers OK if backend not fully async)
- All tests green

**Do NOT in this slice:**
- Do not implement Celery task wiring
- Do not create audit results page
- Do not modify any existing passed tests
- Do not merge any branches

---

## Estimated Complexity

- SEO Issues router: **Low** — model exists, patterns follow existing routers
- Audit endpoints: **Medium** — new router pattern, CLI subprocess integration
- Dashboard wiring: **Low** — follows established wiring pattern from previous slices

**Total estimated files:** 4-6 backend, 3-4 frontend, ~2 doc updates

---

## Branch Recommendation

Work on a new branch: `feature/dashboard-audit-flow`

Branched from current `feature/backend-phase2` HEAD.

---

*Planned: 2025-05-11*
*Planning-only role — no merge, no app code edits*
