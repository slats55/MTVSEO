# Home PC — Dashboard Audit Trigger Flow Plan

**Branch:** `docs/homepc-dashboard-audit-flow-plan`
**Base:** `feature/backend-phase2` @ `18a9504`
**Role:** Planning only — no implementation
**Created:** 2025-05-11

---

## Context

Dashboard API 002 and SEO Issues Router 001 are complete and merged. The dashboard now shows real data for websites, crawl runs, and SEO issues panels.

The remaining gap: **the "Run SEO Audit" and "Run GEO Audit" buttons on the dashboard have no real backend behavior**. Clicking them does nothing诚实.

This plan covers only the **audit trigger flow** — not full audit execution, not Celery workers, not result processing.

---

## Goal

Enable dashboard "Run SEO Audit" and "Run GEO Audit" buttons to create real, honest pending audit job records in the database via real backend endpoints.

---

## What's In Scope

1. **Backend trigger endpoints** — `POST /api/v1/audits/technical` and `POST /api/v1/audits/geo` (or similar) that create a database record with `status=PENDING` and return immediately.
2. **Frontend mutation hooks** — `useTriggerSeoAudit` and `useTriggerGeoAudit` that call those endpoints.
3. **Frontend button wiring** — Dashboard buttons call the mutation hooks.
4. **Honest UI state** — Pending/running/error states shown, never fake completed results.
5. **Real DB records** — Audit jobs stored in the DB, not in-memory.

---

## What's Out of Scope

- Celery/RQ worker implementation (audit execution)
- Fake audit results or scores
- Fake SEO issue generation
- Full audit results page
- GSC/GA4/PageSpeed integrations
- Authentication changes
- Dashboard redesign
- Modifying passed tests

---

## API Route candidates to inspect

The coordinator message suggests these routes as starting points:

- `POST /api/v1/audits/technical`
- `POST /api/v1/audits/geo`
- `POST /api/v1/crawls`
- `POST /api/v1/crawl-runs`
- `POST /api/v1/websites/{website_id}/audits/technical`

**Mr.R9 must inspect existing backend conventions first** before choosing. Do not pick blindly.

Existing patterns to reference:
- `services/api/app/api/v1/` — existing router patterns
- `services/api/app/models/` — existing model patterns (SQLAlchemy 2.x)
- `services/api/app/schemas/` — existing Pydantic schema patterns
- `tests/` — existing test patterns

---

## Request/Response Contract (Draft)

### POST /api/v1/audits/technical (draft)

**Request:**
```json
{
  "website_id": "uuid-string"
}
```

**Response (201):**
```json
{
  "id": "uuid-string",
  "website_id": "uuid-string",
  "audit_type": "technical",
  "status": "PENDING",
  "created_at": "2025-05-11T12:00:00Z",
  "started_at": null,
  "completed_at": null
}
```

**Error (404):**
```json
{
  "detail": "Website not found"
}
```

### POST /api/v1/audits/geo (draft)

Same shape as above with `audit_type: "geo"`.

---

## Frontend Changes

- Add `useTriggerSeoAudit()` hook in `apps/web/src/lib/queries/`
- Add `useTriggerGeoAudit()` hook in `apps/web/src/lib/queries/`
- Add route constants to `apps/web/src/lib/api/routes.ts`
- Wire buttons in `apps/web/src/app/page.tsx`
- Show pending state while job is PENDING/RUNNING
- Show error state on failure
- Do NOT show fake completed results

---

## Verification Checklist

- [ ] `POST /api/v1/audits/technical` returns 201 with PENDING record
- [ ] `POST /api/v1/audits/geo` returns 201 with PENDING record
- [ ] Invalid `website_id` returns 404
- [ ] Audit record exists in DB after POST
- [ ] Dashboard "Run SEO Audit" button calls the endpoint
- [ ] Dashboard "Run GEO Audit" button calls the endpoint
- [ ] UI shows honest pending/running/error state
- [ ] No fake audit results rendered
- [ ] No fake SEO issues generated
- [ ] Existing SEO Issues Router still works (40 tests pass)
- [ ] `python scripts/verify_local.py` passes
- [ ] `pytest tests/ -q` passes
- [ ] `python -m compileall` passes
- [ ] `cd apps/web && npm run build` passes

---

## Rules

1. Do NOT create fake audit results or fake scores
2. Do NOT mark audits complete without real completion logic
3. Do NOT generate fake SEO issues
4. Empty states must be honest
5. Pending/running states must be honest
6. Mr.R9 owns implementation
7. Step Flash owns review
8. Home PC owns planning/docs only

---

## Branch & Commit Strategy

- **Planning branch:** `docs/homepc-dashboard-audit-flow-plan` (this branch)
- **Implementation branch:** `feature/dashboard-audit-trigger-flow-001` (Mr.R9)
- **Base for both:** `origin/feature/backend-phase2` @ `18a9504`
- **No force pushes**
- **No history rewrites**
- **Docs-only on this branch**
