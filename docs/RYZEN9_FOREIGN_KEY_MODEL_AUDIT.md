# Ryzen 9 ForeignKey / Model Relationship Audit

## Audit Context
- **Base branch:** `feature/backend-phase2`
- **Base commit:** `e1bb562` ("Merge Ryzen 9 CRUD API routing fixes")
- **Audit branch:** `audit/ryzen9-foreign-key-model-audit`
- **Purpose:** Audit SQLAlchemy ORM models and Alembic migrations for missing ForeignKey constraints, relationship mismatches, and schema inconsistencies. No implementation changes made.
- **Audit date:** 2026-05-08

---

## Baseline Verification

```
✓ python scripts/verify_local.py — ALL CHECKS PASSED
✓ pytest tests/ -q — 34 passed
✓ python -m compileall services packages tests — no errors
```

---

## Model Inventory

| Model file | Table | Notes |
|-----------|-------|-------|
| `user.py` | `users` | Root entity — no FKs |
| `business.py` | `businesses` | FK: user_id → users |
| `website.py` | `websites` | FK: business_id → businesses |
| `competitor.py` | `competitors` | FK: business_id → businesses |
| `crawl_run.py` | `crawl_runs` | FK: website_id → websites |
| `page.py` | `pages` | FKs: crawl_run_id → crawl_runs, parent_page_id → pages (self-ref) |
| `page_snapshot.py` | `page_snapshots` | FK: page_id → pages (one-to-one) |
| `seo_issue.py` | `seo_issues` | FKs: page_id → pages, crawl_run_id → crawl_runs |
| `geo_issue.py` | `geo_issues` | FKs: page_id → pages, crawl_run_id → crawl_runs |
| `keyword.py` | `keywords` | FK: website_id → websites |
| `topic_cluster.py` | `topic_clusters` | FK: website_id → websites |
| `content_brief.py` | `content_briefs` | FKs: website_id → websites, keyword_id → keywords; column: created_by (no FK) |
| `content_draft.py` | `content_drafts` | FK: content_brief_id → content_briefs; columns: created_by, approved_by (no FKs) |
| `internal_link_opportunity.py` | `internal_link_opportunities` | FKs: website_id → websites, source_page_id → pages, target_page_id → pages |
| `schema_draft.py` | `schema_drafts` | FK: website_id → websites |
| `publishing_job.py` | `publishing_jobs` | FK: content_draft_id → content_drafts; columns: submitted_by, approved_by (no FKs) |
| `report.py` | `reports` | FK: business_id → businesses; column: created_by (no FK) |
| `metric_snapshot.py` | `metric_snapshots` | FK: business_id → businesses |
| `agent_task.py` | `agent_tasks` | columns: business_id, website_id (no FKs); column: created_by (no FK) |
| `agent_run_log.py` | `agent_run_logs` | FK: agent_task_id → agent_tasks |

Migrations inspected:
- `services/api/migrations/versions/20260505_1200_initial_migration.py` (initial — all tables, most FKs)
- `services/api/migrations/versions/20260507_0001_add_agent_task_creator_fk.py` (adds AgentTask.created_by FK)

---

## Confirmed Healthy Constraints

The following FKs are correctly defined in BOTH the ORM model AND the Alembic migration:

| Model | Column | Referenced | Migration |
|-------|--------|-----------|-----------|
| businesses | user_id | users | ✓ initial:129 |
| websites | business_id | businesses | ✓ initial:145 |
| competitors | business_id | businesses | ✓ initial:161 |
| crawl_runs | website_id | websites | ✓ initial:188 |
| pages | crawl_run_id | crawl_runs | ✓ initial:223 |
| pages | parent_page_id | pages (self-ref) | ✓ initial:227 |
| page_snapshots | page_id | pages | ✓ initial:246 |
| seo_issues | page_id | pages | ✓ initial:272 |
| seo_issues | crawl_run_id | crawl_runs | ✓ initial:276 |
| geo_issues | page_id | pages | ✓ initial:302 |
| geo_issues | crawl_run_id | crawl_runs | ✓ initial:306 |
| keywords | website_id | websites | ✓ initial:331 |
| topic_clusters | website_id | websites | ✓ initial:349 |
| content_briefs | website_id | websites | ✓ initial:387 |
| content_briefs | keyword_id | keywords | ✓ initial:391 |
| content_drafts | content_brief_id | content_briefs | ✓ initial:426 |
| internal_link_opportunities | website_id | websites | ✓ initial:458 |
| internal_link_opportunities | source_page_id | pages | ✓ initial:462 |
| internal_link_opportunities | target_page_id | pages | ✓ initial:466 |
| schema_drafts | website_id | websites | ✓ initial:491 |
| publishing_jobs | content_draft_id | content_drafts | ✓ initial:525 |
| reports | business_id | businesses | ✓ initial:555 |
| metric_snapshots | business_id | businesses | ✓ initial:578 |
| agent_tasks | created_by | users | ✓ 20260507_0001 |
| agent_run_logs | agent_task_id | agent_tasks | ✓ initial:626 |

---

## Suspected Missing ForeignKeys

### 1. `agent_task.business_id` — no FK defined in migration

- **Model:** `services/api/models/agent_task.py`
- **Table:** `agent_tasks`
- **Column:** `business_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)`
- **ORM relationship:** `business_id` is nullable and has NO `ForeignKey` in the model
- **Referenced table:** `businesses.id`
- **Migration status:** Column created at initial:588 but no `op.create_foreign_key()` call
- **Severity:** MEDIUM — agent tasks can be orphaned to non-existent businesses; no referential integrity enforcement in PostgreSQL

### 2. `agent_task.website_id` — no FK defined in migration

- **Model:** `services/api/models/agent_task.py`
- **Table:** `agent_tasks`
- **Column:** `business_id` already noted above; `website_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)` is similarly without FK
- **Referenced table:** `websites.id`
- **Migration status:** Column created at initial:589 but no `op.create_foreign_key()` call
- **Severity:** MEDIUM — same as above for websites

### 3. `content_brief.created_by` — no FK defined in migration or model

- **Model:** `services/api/models/content_brief.py`
- **Table:** `content_briefs`
- **Column:** `created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)` (no ForeignKey)
- **Referenced table:** `users.id`
- **Migration status:** Column created at initial:381 but no FK constraint
- **Severity:** LOW — content briefs created without a known user are allowed (null=True)

### 4. `content_draft.created_by` — no FK in migration or model

- **Model:** `services/api/models/content_draft.py`
- **Table:** `content_drafts`
- **Column:** `created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)` (no ForeignKey)
- **Referenced table:** `users.id`
- **Migration status:** Column created at initial:419 but no FK constraint
- **Severity:** LOW — same as above

### 5. `content_draft.approved_by` — no FK in migration or model

- **Model:** `services/api/models/content_draft.py`
- **Table:** `content_drafts`
- **Column:** `approved_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)` (no ForeignKey)
- **Referenced table:** `users.id`
- **Migration status:** Column created at initial:420 but no FK constraint
- **Severity:** LOW — same as above

### 6. `report.created_by` — no FK in migration or model

- **Model:** `services/api/models/report.py`
- **Table:** `reports`
- **Column:** `created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)` (no ForeignKey)
- **Referenced table:** `users.id`
- **Migration status:** Column created at initial:550 but no FK constraint
- **Severity:** LOW — same as above

### 7. `publishing_job.submitted_by` — no FK in migration or model

- **Model:** `services/api/models/publishing_job.py`
- **Table:** `publishing_jobs`
- **Column:** `submitted_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)` (no ForeignKey)
- **Referenced table:** `users.id`
- **Migration status:** Column created at initial:514 but no FK constraint
- **Severity:** LOW — same as above

### 8. `publishing_job.approved_by` — no FK in migration or model

- **Model:** `services/api/models/publishing_job.py`
- **Table:** `publishing_jobs`
- **Column:** `approved_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)` (no ForeignKey)
- **Referenced table:** `users.id`
- **Migration status:** Column created at initial:515 but no FK constraint
- **Severity:** LOW — same as above

---

## Model / Migration Mismatches

### Mismatch Category A: Missing FK constraints (ORM has relationship hint, migration has no FK)

These columns are UUID columns that reference other tables, but neither the ORM model nor the migration defines a `ForeignKey` constraint:

| Model | Column | Should reference | ORM has FK? | Migration has FK? |
|-------|--------|-----------------|-------------|-------------------|
| agent_task | business_id | businesses | NO | NO |
| agent_task | website_id | websites | NO | NO |

### Mismatch Category B: Audit/who columns — soft references with no FK

These `*_by` columns store user IDs but intentionally omit FK constraints to allow null and avoid blocking user deactivation. This is a design choice, not a bug:

| Model | Column | Nullable? | Notes |
|-------|--------|----------|-------|
| content_brief | created_by | YES | Audit trail — intentional no-FK |
| content_draft | created_by | YES | Audit trail — intentional no-FK |
| content_draft | approved_by | YES | Audit trail — intentional no-FK |
| report | created_by | YES | Audit trail — intentional no-FK |
| publishing_job | submitted_by | YES | Audit trail — intentional no-FK |
| publishing_job | approved_by | YES | Audit trail — intentional no-FK |

### Mismatch Category C: ORM ForeignKey exists but migration has no corresponding constraint

No cases found. Every ORM ForeignKey has a corresponding migration constraint, and vice versa.

---

## SQLite vs PostgreSQL Risk

**SQLite does NOT enforce foreign keys by default.** The `foreign_keys` PRAGMA is OFF in most SQLite configurations, including in-memory SQLite used by tests. This means:

1. **Tests silently pass despite missing FK constraints.** `agent_task.business_id` and `agent_task.website_id` can reference non-existent UUIDs without raising errors in test SQLite, but PostgreSQL will throw `foreign_key_violation` errors at runtime.

2. **No referential integrity in SQLite test DB.** Code that would fail in production with a bad `business_id` on an `AgentTask` passes all local tests because SQLite never checks the constraint.

3. **SQLAlchemy inspects but does not enforce.** Even with `checkfirst=True`, Alembic and SQLAlchemy do not enforce FK constraints at query time — they only define them in the DDL. SQLite ignores them unless `PRAGMA foreign_keys = ON` is set.

4. **Nullable FKs reduce blast radius.** Since `agent_task.business_id` and `agent_task.website_id` are nullable, a row can be inserted without a FK violation if the value is NULL. But if a non-NULL invalid UUID is inserted, PostgreSQL enforces the constraint and throws. In SQLite tests, this would silently succeed.

**Practical impact:** The two missing FKs (agent_task.business_id, agent_task.website_id) are the only ones that could cause PostgreSQL runtime errors in normal usage. The `*_by` audit columns are all nullable and intentionally unconstrained.

---

## Relationship Completeness Check

| Parent model | Relationship | Child/backref | back_populates | Status |
|-------------|-------------|---------------|----------------|--------|
| User | businesses | Business.user | back_populates="user" | ✓ |
| User | agent_tasks | AgentTask.creator | back_populates="creator" | ✓ |
| Business | websites | Website.business | back_populates="business" | ✓ |
| Business | competitors | Competitor.business | back_populates="business" | ✓ |
| Business | metric_snapshots | MetricSnapshot.business | back_populates="business" | ✓ |
| Business | reports | Report.business | back_populates="business" | ✓ |
| Website | crawl_runs | CrawlRun.website | back_populates="website" | ✓ |
| Website | keywords | Keyword.website | back_populates="website" | ✓ |
| Website | topic_clusters | TopicCluster.website | back_populates="website" | ✓ |
| Website | schema_drafts | SchemaDraft.website | back_populates="website" | ✓ |
| Website | internal_link_opportunities | InternalLinkOpportunity.website | back_populates="website" | ✓ |
| CrawlRun | pages | Page.crawl_run | back_populates="pages" | ✓ |
| CrawlRun | seo_issues | SeoIssue.crawl_run | back_populates="crawl_run" | ✓ |
| CrawlRun | geo_issues | GeoIssue.crawl_run | back_populates="geo_issues" | ✓ |
| Page | seo_issues | SeoIssue.page | back_populates="seo_issues" | ✓ |
| Page | geo_issues | GeoIssue.page | back_populates="geo_issues" | ✓ |
| Page | snapshot | PageSnapshot.page | back_populates="snapshot" | ✓ |
| Page | parent_page | Page.parent_page_id | (self-ref, no back_populates) | ✓ |
| ContentBrief | drafts | ContentDraft.brief | back_populates="drafts" | ✓ |
| ContentBrief | website | Website (no back_populates on Website) | N/A | ⚠ |
| ContentDraft | brief | ContentBrief.drafts | back_populates="drafts" | ✓ |
| ContentDraft | publishing_jobs | PublishingJob.draft | back_populates="draft" | ✓ |
| AgentTask | run_logs | AgentRunLog.task | back_populates="task" | ✓ |
| Keyword | content_briefs | ContentBrief.keyword | back_populates="keyword" | ✓ |

**⚠ Note:** `ContentBrief.website` relationship uses `relationship("Website")` without `back_populates` on the Website side. The Website model does not have a `content_briefs` backref. This is a one-way relationship — it works functionally but is asymmetric with the rest of the codebase convention.

---

## Recommended Fix Plan

### High Priority — Add missing FK constraints

**Do these first; they affect PostgreSQL production correctness:**

1. **Add FK: `agent_tasks.business_id` → `businesses.id`**
   - File: `services/api/models/agent_task.py`
   - Add `ForeignKey("businesses.id", ondelete="SET NULL")` to the `business_id` column
   - Create new migration: `services/api/migrations/versions/YYYYMMDD_HHMM_add_agent_task_business_website_fk.py`
   - Migration: `op.add_constraint("fk_agent_tasks_business_id", ...)` on `business_id` column
   - Index `ix_agent_tasks_business_id` is already created at initial:605

2. **Add FK: `agent_tasks.website_id` → `websites.id`**
   - File: `services/api/models/agent_task.py`
   - Add `ForeignKey("websites.id", ondelete="SET NULL")` to the `website_id` column
   - Index `ix_agent_tasks_website_id` is already created at initial:606

### Medium Priority — ORM symmetry

3. **Fix asymmetric relationship on ContentBrief.website**
   - Add `content_briefs = relationship("ContentBrief", back_populates="website")` to `Website` model
   - Or change `ContentBrief.website` to use `back_populates` targeting the new Website backref
   - No migration needed — ORM only

### Low Priority — Audit trail columns (design decision)

These nullable `*_by` columns intentionally have no FK to allow user deactivation without blocking records. This is a valid design pattern. **No fix needed** — document the pattern instead.

---

## Files to Modify

| File | Change | Migration needed? |
|------|--------|-------------------|
| `services/api/models/agent_task.py` | Add `ForeignKey("businesses.id")` to `business_id`, `ForeignKey("websites.id")` to `website_id` | YES |
| `services/api/models/website.py` | Add `content_briefs` back_populates relationship (optional symmetry fix) | NO |
| `services/api/migrations/versions/<new>.py` | Add FK constraints for agent_task.business_id and agent_task.website_id | N/A |

---

## Tests to Add

| Test | Purpose |
|------|---------|
| `test_agent_task_business_id_fk` | Verify inserting AgentTask with non-existent business_id raises IntegrityError on PostgreSQL |
| `test_agent_task_website_id_fk` | Same for website_id |
| `test_agent_task_null_business_id_allowed` | Verify NULL business_id is accepted (nullable=True) |
| Verify these skip on SQLite (xfail) since SQLite doesn't enforce FKs | PostgreSQL-only constraints that SQLite cannot test |

---

## Verification Commands

```bash
# Verify models import cleanly
.venv/bin/python -c "from services.api.models import *; print('OK')"

# Verify migration files are valid Python
.venv/bin/python -m compileall services/api/migrations/versions

# Run full test suite (should pass 34/34 before and after FK additions)
.venv/bin/python -m pytest tests/ -q

# For PostgreSQL-only FK test (skip on SQLite):
# pytest tests/ -k "fk" -m "not sqlite" --tb=short
```

---

## Final Verdict

**FIX REQUIRED BEFORE NEXT BACKEND SLICE — non-blocking but important.**

The `agent_task.business_id` and `agent_task.website_id` columns are missing `ForeignKey` constraints in both the ORM model and the Alembic migration. These columns can accept arbitrary UUIDs in PostgreSQL without referential integrity, creating a risk of orphaned agent task records pointing to non-existent businesses or websites.

The `*_by` audit columns (created_by, approved_by, submitted_by across content_draft, content_brief, report, publishing_job) are intentionally nullable without FK constraints — this is a valid design choice to prevent user deactivation from blocking historical records. No fix needed for those.

The asymmetric `ContentBrief.website` relationship is a medium-priority ORM hygiene issue — functional but inconsistent with codebase conventions.

**Summary of required actions:**
- 2 FK constraints to add (agent_task.business_id, agent_task.website_id) — requires migration
- 1 ORM relationship to symmetrize (ContentBrief.website back_populates) — no migration
- 8 `*_by` audit columns — no action needed (design decision documented)
- All other FKs, relationships, and constraints — already correct in both ORM and migration

**The schema is largely correct.** The issues above are surgical and well-scoped.