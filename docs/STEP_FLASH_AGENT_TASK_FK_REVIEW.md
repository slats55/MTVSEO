# Step Flash AgentTask ForeignKey Review

**Review Date:** 2026-05-08
**Reviewer:** Step Flash (gatekeeper)
**Project:** MTVSEO — Autonomous SEO Agent OS

## Review Target

- **Base branch:** `feature/backend-phase2`
- **Base commit:** `e1bb562` — Merge Ryzen 9 CRUD API routing fixes
- **Target branch:** `origin/fix/ryzen9-agent-task-foreign-keys`
- **Target commit:** `5948dcf` — fix(models): add AgentTask business and website foreign keys

## Executive Verdict

**PASS WITH DATA NOTE** — ready to merge, but orphan-data risk should be known and addressed before production deployment.

All verification checks pass, the migration is structurally sound, and the changes are narrowly scoped to the identified problem. The foreign key constraints correctly enforce referential integrity with `ON DELETE SET NULL` behavior.

## Verification Results

| Check | Result |
|-------|--------|
| `python scripts/verify_local.py` | ✅ ALL CHECKS PASSED |
| `pytest tests/test_endpoint_crud.py -q` | ✅ 12 passed |
| `pytest tests/ -q` | ✅ 34 passed |
| `python -m compileall services packages tests` | ✅ No errors |
| `alembic heads` (via `services/api/alembic.ini`) | ✅ `20260508_0001` (head) |

## Diff Summary

**Total changed files:** 4 files (190 insertions, 4 deletions)

- `services/api/models/agent_task.py` — Added `ForeignKey` constraints on `business_id` and `website_id`
- `services/api/migrations/versions/20260508_0001_add_agent_task_business_website_fk.py` — New migration adding the FK constraints
- `tests/test_alembic_smoke.py` — Updated expected head revision from `20260507_0001` to `20260508_0001`
- `docs/RYZEN9_AGENT_TASK_FK_FIX.md` — Documentation of the fix (not merged into codebase)

## Model Review

✅ **AgentTask model changes are correct:**

```python
business_id: Mapped[uuid.UUID | None] = mapped_column(
    Uuid,
    ForeignKey("businesses.id", ondelete="SET NULL"),
    nullable=True,
)
website_id: Mapped[uuid.UUID | None] = mapped_column(
    Uuid,
    ForeignKey("websites.id", ondelete="SET NULL"),
    nullable=True,
)
```

- Both columns retain `nullable=True` (existing NULL values allowed)
- `ondelete="SET NULL"` matches nullable design — when referenced business/website is deleted, the task is preserved rather than cascaded delete
- Uses the same `Uuid` type as the rest of the codebase (SQLAlchemy 2.0 compatible)
- No other columns modified; relationship patterns preserved

## Migration Review

✅ **Migration `20260508_0001` is correct:**

- **Revision chain:** `down_revision="20260507_0001"` (proper linear chain)
- **Upgrade:** Adds two `op.create_foreign_key()` constraints with `ondelete="SET NULL"`
- **Downgrade:** Drops both constraints (reversed order to avoid drop dependencies)
- **No data modification:** Only adds constraints; does not delete or alter any rows
- **Idempotency:** `create_foreign_key` will fail if constraints already exist; safe for fresh databases
- **Naming:** Constraint names follow existing pattern (`fk_agent_tasks_<column>`)

## Orphan Data Risk Review

⚠️ **Known risk, documented, and acceptable for current phase.**

The migration will **fail** if any `agent_tasks` rows have non-NULL `business_id` or `website_id` that reference non-existent `businesses.id` or `websites.id`. This is intentional — the migration surfaces data integrity issues rather than silently ignoring them.

**Mitigation required before production deployment:**
1. Run cleanup query to identify orphaned rows
2. Either delete them or set the FK column to NULL
3. Then re-run the migration

Given this is a Phase 2 development branch and likely running on fresh or test data, the risk is minimal. The branch is safe to merge; deployment teams should be aware of the pre-migration cleanup requirement.

**Does this block merge?** **No** — the risk is a deployment concern, not a code correctness issue. Mark as `PASS WITH DATA NOTE` to surface the awareness.

## Branch Hygiene

✅ **No unrelated changes:**

- No frontend files modified
- No changes to `services/api/routers/` or `services/api/schemas/`
- No ContentBrief relationship changes (deferred as documented)
- Only the specific AgentTask FK issue addressed
- Commit message and documentation align with the narrow fix

## Merge Recommendation

**MERGE INTO feature/backend-phase2 NOW**

The branch is:
- Correctly implemented (model + migration)
- Fully tested (all 34 tests pass)
- Alembic head shows the new migration
- No side effects or unrelated refactors
- Narrowly scoped to the audit finding

## Recommended Next Step

```bash
# From the review branch or any clean branch
git checkout feature/backend-phase2
git pull origin feature/backend-phase2
git merge --no-ff origin/fix/ryzen9-agent-task-foreign-keys -m "Merge AgentTask foreign key constraints (business_id, website_id)"
git push origin feature/backend-phase2
```

Deployment teams should read `docs/RYZEN9_AGENT_TASK_FK_FIX.md` and perform orphan-data cleanup before applying this migration to production databases with existing `agent_tasks` data.

---

Signed,
Step Flash (gatekeeper)
MTVSEO Phase 2 Workflow

**Status:** Approved for merge with data note ⚠️
