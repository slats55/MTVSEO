# Ryzen 9 AgentTask ForeignKey Fix

## Purpose

This branch implements the high-priority FK findings from the Ryzen 9 ForeignKey / Model Relationship Audit (`audit/ryzen9-foreign-key-model-audit`, commit `e6d9d33`).

Two columns on `agent_tasks` were missing `ForeignKey` constraints in both the ORM model and the Alembic migration, allowing PostgreSQL to accept orphaned references to non-existent `businesses.id` or `websites.id` rows.

---

## Branch Context

- **Base branch:** `feature/backend-phase2`
- **Base commit:** `e1bb562` ("Merge Ryzen 9 CRUD API routing fixes")
- **Fix branch:** `fix/ryzen9-agent-task-foreign-keys`
- **Audit source:** `origin/audit/ryzen9-foreign-key-model-audit` (commit `e6d9d33`)
- **Auditor:** Ryzen 9 MiniMax Hermes Agent
- **Implementation date:** 2026-05-08

---

## Changes Made

### Model changes: `services/api/models/agent_task.py`

- `business_id` column: added `ForeignKey("businesses.id", ondelete="SET NULL")`
- `website_id` column: added `ForeignKey("websites.id", ondelete="SET NULL")`
- Nullable behavior preserved (`nullable=True` on both — existing rows with NULL values remain valid)
- No other columns modified

### Migration file added

- `services/api/migrations/versions/20260508_0001_add_agent_task_business_website_fk.py`
- Revises: `20260507_0001` (the previous AgentTask.created_by FK migration)
- Adds two `op.create_foreign_key()` calls: one for `business_id → businesses.id`, one for `website_id → websites.id`
- Both use `ondelete="SET NULL"` to match the nullable=True column definition
- Downgrade drops both constraints (order reversed to avoid dependency issues)

### Test file updated

- `tests/test_alembic_smoke.py`: updated `test_alembic_heads_discovers_migration` to assert the new head `20260508_0001` instead of the old head `20260507_0001`
- No new test files added (existing test pattern was directly applicable)
- All 34 tests pass: 12 CRUD + 22 others (alembic_smoke, endpoint_smoke, uvicorn, conftest)

---

## ForeignKeys Added

| Column | Table (from) | References (to) | ondelete | Nullable preserved? |
|--------|-------------|-----------------|----------|--------------------|
| `agent_tasks.business_id` | `agent_tasks` | `businesses.id` | SET NULL | YES — nullable=True unchanged |
| `agent_tasks.website_id` | `agent_tasks` | `websites.id` | SET NULL | YES — nullable=True unchanged |

---

## Migration Notes

### Upgrade behavior

The upgrade adds two `CREATE FOREIGN KEY` constraints to the `agent_tasks` table. Since both referenced columns (`business_id`, `website_id`) are nullable, existing rows with NULL values in those columns will not block the migration.

### Downgrade behavior

The downgrade drops both FK constraints using `op.drop_constraint()`. This is a metadata-only change — no data is deleted.

### Orphaned data risk (production)

**WARNING:** If production PostgreSQL data contains `agent_tasks` rows where `business_id` or `website_id` is non-NULL but references a `businesses.id` or `websites.id` that no longer exists, this migration will fail with a `foreign_key_violation` error.

This is the intended behavior — it surfaces data integrity issues rather than silently fixing them.

If this migration fails in production due to orphaned rows, the corrective action is:
1. Identify orphaned rows: `SELECT * FROM agent_tasks WHERE business_id NOT IN (SELECT id FROM businesses) OR website_id NOT IN (SELECT id FROM websites);`
2. Decide whether to set them to NULL or delete them
3. Apply that cleanup before re-running this migration

**No destructive cleanup was performed in this migration.** The migration is designed to be safe to downgrade and does not delete or modify any data.

---

## Verification Results

```
python scripts/verify_local.py       ✓ ALL CHECKS PASSED
pytest tests/test_endpoint_crud.py    ✓ 12 passed in 1.08s
pytest tests/                        ✓ 34 passed in 1.94s (0 failed)
python -m compileall                 ✓ no errors
alembic heads                        ✓ 20260508_0001 (head)
```

---

## Deferred Items

The following items from the audit are intentionally deferred to future branches:

1. **ContentBrief.website asymmetric relationship** — `ContentBrief.website` uses `relationship("Website")` without `back_populates` on the `Website` model. No `back_populates` relationship exists on the Website side. This is a medium-priority ORM hygiene issue, not a schema correctness issue. Deferred to a future low-impact ORM symmetry branch.

2. **Audit trail columns** (`created_by`, `approved_by`, `submitted_by` on content_brief, content_draft, report, publishing_job) — these are intentionally nullable without FK constraints to allow user deactivation without blocking historical records. This is a valid design pattern. No action needed; pattern documented in audit report.

3. **ContentBrief, ContentDraft FK columns** — already have correct FKs in migration (`fk_content_briefs_website_id`, `fk_content_drafts_content_brief_id`).

---

## Recommended Next Step

**Step Flash should review `fix/ryzen9-agent-task-foreign-keys` before merge into `feature/backend-phase2`.**

Review checklist:
- Confirm `agent_task.py` ForeignKey additions are correct and style-consistent
- Confirm migration `20260508_0001` has valid upgrade/downgrade paired correctly
- Confirm `test_alembic_smoke.py` assertion update is appropriate
- Run `alembic validate --config services/api/alembic.ini` if environment supports it
- Verify no other files were modified beyond the intended scope