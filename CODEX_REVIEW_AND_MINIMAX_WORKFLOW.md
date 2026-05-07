# Codex Review & MiniMax Workflow — MTVSEO

## 1. Executive Summary
Current repository state is **not an MVP and not a working skeleton**; it is effectively an empty bootstrap with a single `README.md` containing only the project name (`# MTVSEO`) and no application/runtime code.

**Facts validated:**
- No backend, frontend, packages, docs, tests, scripts, or env template directories/files are present.
- No remote is configured in this local git clone, so branch comparison against `main`, `master`, `dev`, or `chore/stabilize-runtime` is impossible from this environment.
- There is one local branch (`work`) and one commit (`Initial commit`).
- Python compile pass is trivial because there are no Python modules.
- Pytest runs but discovers zero tests.

Bottom line: this repo is currently **initialization-only**, with **100% of the intended product still to be implemented**.

## 2. Recommended Working Branch
**Recommended branch for MiniMax next session:** `work` (current local branch), only as a temporary baseline.

### Why
- It is the only available local branch.
- No remotes are configured, so the required branch health check (`main`, `master`, `dev`, `chore/stabilize-runtime`) cannot be completed.

### Branch cleanup recommendation
1. First fix git remote connectivity (`origin`) and fetch all branches.
2. Re-run branch inventory and compare commit deltas between `main`, `master`, `dev`, `chore/stabilize-runtime`, and `work`.
3. Select canonical base branch (likely `main` or `dev`) and either:
   - fast-forward it from the most complete branch, or
   - merge the most complete branch into canonical default.
4. Rename/remove `work` after canonical alignment.

## 3. Current System Inventory

| Area | Current Status | Real / Placeholder / Missing | Notes |
|---|---|---|---|
| Frontend | No `apps/web` present | Missing | No UI code found. |
| Backend API | No `services/api` present | Missing | No FastAPI app, routes, or startup module. |
| Database models | None found | Missing | No ORM models or schema files. |
| Migrations | None found | Missing | No Alembic config or migration tree. |
| Crawler | None found | Missing | No crawler modules, configs, or persistence. |
| SEO audit | None found | Missing | No analyzers/scoring code. |
| GEO audit | None found | Missing | No llms.txt / AI visibility engine code. |
| Content engine | None found | Missing | No brief/draft workflow code. |
| Schema engine | None found | Missing | No JSON-LD generation/validation logic. |
| Reporting | None found | Missing | No report generation pipeline. |
| Integrations | No `packages` directory present | Missing | No GSC/GA4/PageSpeed/etc. integration layer. |
| Queue/workers | None found | Missing | No Celery/RQ/worker scaffold. |
| Tests | `pytest` available but no tests discovered | Placeholder | Test framework exists in environment only. |
| Docs | Only minimal `README.md` | Placeholder | No architecture/runbook/handoff docs. |
| Config/env | No `.env.example` present | Missing | No documented runtime config contract. |

## 4. Validation Results

| Command | Result | Notes / Error |
|---|---|---|
| `git status` | Pass | Clean tree on branch `work`. |
| `git branch -a` | Pass | Only `work` exists locally. |
| `git log --oneline --decorate --graph --all -n 30` | Pass | Single commit: `Initial commit`. |
| `git remote -v` | Pass | No remotes configured; cannot fetch remote branches. |
| `git fetch --all --prune` | Pass (no-op) | No remotes to fetch from. |
| `python -m compileall .` | Pass | No meaningful source files compiled. |
| `pytest` | Fail (MVP validation fail) | Exit code 5: no tests collected. MiniMax should add baseline smoke tests. |
| `test -f AGENT_HANDOFF.md` | Fail | Missing required handoff doc. |
| `test -d docs` | Fail | Missing docs directory. |
| `test -d services/api` | Fail | Missing backend app tree. |
| `test -d packages` | Fail | Missing integration/shared packages tree. |
| `test -d apps/web` | Fail | Missing frontend app tree. |
| `test -d tests` | Fail | Missing tests folder in repository. |
| `test -d scripts` | Fail | Missing automation scripts. |
| `test -f .env.example` | Fail | Missing environment template. |

## 5. Major Gaps Blocking MVP
Priority ordered by requested dimensions.

1. **Runtime stability blocker:** No runnable codebase exists.
2. **API/backend usability blocker:** No FastAPI service, no endpoints, no health route.
3. **Real data-flow blocker:** No database schema/models/migrations.
4. **Dashboard blocker:** No frontend scaffold and no API client.
5. **Pipeline blocker:** No crawl → audit → report implementation at all.
6. **Human-review safety blocker:** No approval workflow constructs for content/publication.
7. **Testing blocker:** No test suite, fixtures, or green-build definition.

## 6. Product Architecture Recommendation
Practical near-term architecture to build from zero without over-engineering.

### Backend/API structure
- `services/api` (FastAPI monolith for MVP):
  - `main.py` app bootstrap
  - `routers/` for businesses, sites, crawl runs, audits, reports, content approvals
  - `schemas/` (Pydantic request/response)
  - `models/` (SQLAlchemy ORM)
  - `services/` (crawl orchestration, audit engine orchestration, report builder)
  - `core/` config, logging, db session

### Background task flow
- Start with **RQ + Redis** or **Celery + Redis** (pick one; RQ simpler for MVP).
- API creates job rows and enqueues tasks.
- Worker executes crawl then audit then report pipeline stages.
- Persist stage/status transitions in DB.

### Database persistence flow
- PostgreSQL for MVP (SQLite acceptable only for local smoke).
- Core entities: Business, Website, CrawlRun, Page, AuditRun, Issue, Report, ContentDraft, ApprovalTask, Job.
- Add idempotent migrations with Alembic from day 1.

### Frontend data flow
- `apps/web` (Next.js or Vite React):
  - SSR/CSR hybrid acceptable.
  - API client module with typed endpoints.
  - MVP screens: Businesses, Sites, Crawl Runs, Audit Results, Reports, Approvals.

### Package/module boundaries
- `packages/core` shared types/utilities.
- `packages/integrations` for external APIs.
- `packages/engines` optional later split for crawler/audit/geo once stable.

### Local dev workflow
- `docker-compose` for Postgres + Redis.
- `make`/`just` commands: `setup`, `api`, `worker`, `web`, `test`, `lint`.
- `.env.example` with explicit required variables.

### MVP deployment assumptions
- Single backend container + single worker + Postgres + Redis.
- No autonomous publishing in MVP.
- Human approval required for any content export/publish action.

## 7. MiniMax Implementation Roadmap

### Phase A — Stabilize Repository and Runtime
Goal:
Create a runnable baseline repo with backend scaffold, config, docs, and repeatable local startup.

Tasks:
- Add directory structure (`services/api`, `apps/web`, `packages`, `tests`, `scripts`, `docs`).
- Add `.env.example`, `pyproject.toml` (or `requirements.txt`), and root `README` runtime steps.
- Add FastAPI health endpoint and DB connectivity skeleton.
- Add AGENT_HANDOFF.md template.

Files likely affected:
- `README.md`, `AGENT_HANDOFF.md`, `.env.example`, `services/api/**`, `tests/**`, `docs/**`, `scripts/**`.

Definition of done:
- API boots locally.
- `/health` returns 200.
- Basic test command runs and passes at least 1 smoke test.

Validation commands:
- `python -m compileall services/api`
- `pytest -q`
- `uvicorn services.api.main:app --host 0.0.0.0 --port 8000`

### Phase B — Connect Crawl → Audit → Report Pipeline
Goal:
Implement minimal end-to-end pipeline with persisted artifacts.

Tasks:
- Add crawl run model + page model.
- Implement safe crawler MVP (domain boundary, robots check, limits/timeouts).
- Implement technical audit engine over crawled pages.
- Implement markdown report generation and persistence.

Files likely affected:
- `services/api/models/**`, `services/api/services/crawler/**`, `services/api/services/audit/**`, `services/api/services/reporting/**`, `tests/**`.

Definition of done:
- One API request can trigger crawl+audit+report for a test site.
- Report record retrievable via API.

Validation commands:
- `pytest -q tests/pipeline`
- `python scripts/run_local_pipeline_smoke.py`

### Phase C — API Job Orchestration
Goal:
Move long-running pipeline to background jobs with status tracking.

Tasks:
- Add `jobs` table and status enum.
- Implement queue producer/worker consumer.
- Add API endpoints for job creation/status polling.

Files likely affected:
- `services/api/routers/jobs.py`, `services/api/services/jobs/**`, `services/api/workers/**`, `services/api/models/**`, `tests/**`.

Definition of done:
- Pipeline executes async and status transitions are visible.

Validation commands:
- `pytest -q tests/jobs`
- `python scripts/smoke_jobs.py`

### Phase D — Dashboard API Integration
Goal:
Build minimal web dashboard connected to real API data.

Tasks:
- Scaffold frontend app and API client.
- Implement pages for businesses/sites/runs/reports.
- Add job polling UI and result rendering.

Files likely affected:
- `apps/web/**`, `services/api/routers/**`, `packages/core/**`, `tests/**`.

Definition of done:
- User can create run and view report in UI.

Validation commands:
- `npm run build`
- `npm run test`

### Phase E — Content / Schema / GEO Workflow
Goal:
Add compliance-first assisted generation features with human approval gate.

Tasks:
- Add content brief generator with source citation requirements.
- Add schema JSON-LD generator for LocalBusiness + Service + FAQ baseline.
- Add GEO checks (llms.txt suggestion, AI crawlability checks).
- Add mandatory approval status before publish/export.

Files likely affected:
- `services/api/services/content/**`, `services/api/services/schema/**`, `services/api/services/geo/**`, `services/api/models/**`, `apps/web/**`, `tests/**`.

Definition of done:
- Content/schema/geo outputs generated but cannot publish without explicit approval.

Validation commands:
- `pytest -q tests/content tests/schema tests/geo`

### Phase F — Integrations Foundation
Goal:
Add pluggable integration stubs and one real low-cost integration.

Tasks:
- Define integration interface/contracts.
- Implement PageSpeed first (public API with manageable auth complexity).
- Add placeholders for GSC/GA4/WordPress/GitHub with feature flags.

Files likely affected:
- `packages/integrations/**`, `services/api/services/integrations/**`, `docs/integrations.md`, `tests/**`.

Definition of done:
- One working integration with persisted output and retry behavior.

Validation commands:
- `pytest -q tests/integrations`

### Phase G — Production Readiness
Goal:
Harden quality, safety, observability, and deployment baseline.

Tasks:
- Add structured logging, request IDs, and error taxonomy.
- Add CI workflow for lint + tests.
- Add rate limiting and abuse protections.
- Add compliance policy checks for cannabis/YMYL workflows.

Files likely affected:
- `.github/workflows/**`, `services/api/core/**`, `services/api/middleware/**`, `docs/security.md`, `tests/**`.

Definition of done:
- Repeatable CI green path and documented operational guardrails.

Validation commands:
- `pytest -q`
- `npm run build`
- `python scripts/verify_local.py`

## 8. MiniMax Task Queue

### MM-001 — Normalize Branch and Remote Baseline
Objective:
Establish real branch topology and canonical base branch.
Files to inspect:
- `.git/config`, remote branches, default branch metadata.
Files likely to change:
- `AGENT_HANDOFF.md`.
Implementation notes:
- Configure/fix `origin`, fetch all, compare `main/master/dev/chore/stabilize-runtime`.
Safety notes:
- No rebases/force pushes.
Acceptance criteria:
- Branch comparison documented with recommended base branch.
Test command:
- `git remote -v && git fetch --all --prune && git branch -a`

### MM-002 — Create Runtime Skeleton
Objective:
Add required project directories and baseline files.
Files to inspect:
- `README.md`.
Files likely to change:
- `services/api/**`, `apps/web/**`, `packages/**`, `tests/**`, `scripts/**`, `.env.example`.
Implementation notes:
- Keep modules minimal and runnable.
Safety notes:
- No placeholder secrets.
Acceptance criteria:
- Tree exists and is coherent.
Test command:
- `rg --files`

### MM-003 — FastAPI App Bootstrap + Health Route
Objective:
Make API boot successfully with `/health`.
Files to inspect:
- `services/api/main.py`.
Files likely to change:
- `services/api/main.py`, `services/api/routers/health.py`.
Implementation notes:
- Include app startup/shutdown lifecycle hooks.
Safety notes:
- No network side effects on startup.
Acceptance criteria:
- Health endpoint returns 200 JSON.
Test command:
- `uvicorn services.api.main:app --port 8000`

### MM-004 — DB Session + Base Models
Objective:
Add SQLAlchemy setup and foundational entities.
Files to inspect:
- `services/api/core/config.py`.
Files likely to change:
- `services/api/core/db.py`, `services/api/models/**`.
Implementation notes:
- Add Business, Website, CrawlRun, Page, AuditRun, Report, Job.
Safety notes:
- Default to local-safe DB URL.
Acceptance criteria:
- Models import cleanly.
Test command:
- `python -m compileall services/api`

### MM-005 — Alembic Initialization
Objective:
Enable reproducible schema migrations.
Files to inspect:
- `services/api/models/**`.
Files likely to change:
- `alembic.ini`, `alembic/**`.
Implementation notes:
- Create initial migration from models.
Safety notes:
- Avoid destructive downgrade assumptions.
Acceptance criteria:
- Migration applies on empty DB.
Test command:
- `alembic upgrade head`

### MM-006 — Crawl Safety MVP
Objective:
Implement bounded crawler with respect rules.
Files to inspect:
- crawler service modules.
Files likely to change:
- `services/api/services/crawler/**`.
Implementation notes:
- Enforce robots check, per-domain scope, max pages, timeout.
Safety notes:
- Never cross-domain by default.
Acceptance criteria:
- Crawl returns deterministic page list on test site.
Test command:
- `pytest -q tests/crawler`

### MM-007 — Persist Crawl Output
Objective:
Store page and crawl metadata to DB.
Files to inspect:
- crawl models and service contracts.
Files likely to change:
- `services/api/models/page.py`, `services/api/services/crawler/persist.py`.
Implementation notes:
- Include status code, canonical URL, title/meta basics.
Safety notes:
- Sanitize stored HTML payload length.
Acceptance criteria:
- Crawl run + pages queryable via API.
Test command:
- `pytest -q tests/crawler tests/api`

### MM-008 — Technical Audit Engine MVP
Objective:
Run actionable technical SEO checks over crawled pages.
Files to inspect:
- audit service design.
Files likely to change:
- `services/api/services/audit/**`, `services/api/models/audit*.py`.
Implementation notes:
- Checks: title, meta description, headings, status, indexability.
Safety notes:
- Keep scoring transparent and deterministic.
Acceptance criteria:
- Audit run creates issues and score.
Test command:
- `pytest -q tests/audit`

### MM-009 — Report Generator MVP
Objective:
Generate markdown summary from audit/crawl data.
Files to inspect:
- reporting services.
Files likely to change:
- `services/api/services/reporting/**`, `services/api/models/report.py`.
Implementation notes:
- Prioritize top issues and quick wins.
Safety notes:
- Mark generated recommendations as suggestions.
Acceptance criteria:
- Report saved and retrievable.
Test command:
- `pytest -q tests/reporting`

### MM-010 — Pipeline Orchestrator Endpoint
Objective:
Expose endpoint that triggers crawl→audit→report.
Files to inspect:
- routers and service layer.
Files likely to change:
- `services/api/routers/pipeline.py`, `services/api/services/pipeline.py`.
Implementation notes:
- Return run ID and status.
Safety notes:
- Validate input URL and business ownership.
Acceptance criteria:
- Endpoint executes and returns run artifacts.
Test command:
- `pytest -q tests/pipeline`

### MM-011 — Queue + Worker Baseline
Objective:
Move pipeline execution off request thread.
Files to inspect:
- job orchestration modules.
Files likely to change:
- `services/api/workers/**`, `services/api/services/jobs/**`.
Implementation notes:
- Implement queued job states: queued/running/succeeded/failed.
Safety notes:
- Retry cap to avoid runaway jobs.
Acceptance criteria:
- Background execution works with status polling.
Test command:
- `pytest -q tests/jobs`

### MM-012 — Frontend Scaffold + API Client
Objective:
Create basic dashboard app consuming live API.
Files to inspect:
- frontend setup and scripts.
Files likely to change:
- `apps/web/**`.
Implementation notes:
- Centralized API client and typed DTOs.
Safety notes:
- No direct secret exposure client-side.
Acceptance criteria:
- UI can list runs/reports.
Test command:
- `npm run build`

### MM-013 — Human Approval Gate
Objective:
Enforce manual approval before content publish/export.
Files to inspect:
- content/report endpoints.
Files likely to change:
- `services/api/models/approval.py`, `services/api/routers/content.py`, `apps/web/**`.
Implementation notes:
- Approval status must gate publish actions.
Safety notes:
- Default deny.
Acceptance criteria:
- Publish blocked without explicit approval.
Test command:
- `pytest -q tests/approval`

### MM-014 — GEO + llms.txt Advisory MVP
Objective:
Add basic AI visibility recommendations.
Files to inspect:
- geo service modules.
Files likely to change:
- `services/api/services/geo/**`.
Implementation notes:
- Generate advisory llms.txt template, do not auto-deploy.
Safety notes:
- Human review required.
Acceptance criteria:
- GEO audit output visible in report/API.
Test command:
- `pytest -q tests/geo`

### MM-015 — Schema JSON-LD Generator MVP
Objective:
Generate and validate local SEO schema drafts.
Files to inspect:
- schema services and models.
Files likely to change:
- `services/api/services/schema/**`.
Implementation notes:
- Support LocalBusiness, Service, FAQPage first.
Safety notes:
- Mark as draft until approved.
Acceptance criteria:
- JSON-LD draft + validation result stored.
Test command:
- `pytest -q tests/schema`

### MM-016 — Baseline Integration Contract + PageSpeed
Objective:
Ship one real integration behind common interface.
Files to inspect:
- integration package boundary.
Files likely to change:
- `packages/integrations/**`, `services/api/services/integrations/**`.
Implementation notes:
- Add adapter pattern and retry/error normalization.
Safety notes:
- Respect API quota and terms.
Acceptance criteria:
- PageSpeed fetch persists metrics for a URL.
Test command:
- `pytest -q tests/integrations`

### MM-017 — QA Green Build Definition
Objective:
Define and enforce repeatable green build.
Files to inspect:
- CI config and local verify scripts.
Files likely to change:
- `.github/workflows/ci.yml`, `scripts/verify_local.py`, `README.md`.
Implementation notes:
- Single command should validate compile+tests+build.
Safety notes:
- Fail fast on any red check.
Acceptance criteria:
- CI passes on clean branch.
Test command:
- `python scripts/verify_local.py`

## 9. What MiniMax Should NOT Do Yet
- Do **not** implement autonomous publishing to live sites yet; approval and audit controls are not in place.
- Do **not** add paid or quota-heavy integrations (full GSC/GA4 sync) before local crawl/audit/report pipeline is stable.
- Do **not** build complex multi-agent orchestration until single pipeline execution is deterministic.
- Do **not** introduce enterprise auth/RBAC before basic single-operator workflow works.
- Do **not** perform large UI redesign before API and data models are stable.
- Do **not** over-split into microservices; keep MVP in one backend service.

## 10. Suggested Definition of Done for Next MiniMax Session
- Remote configured and branch topology documented.
- Repository contains runnable baseline structure.
- API starts locally and `/health` returns success.
- DB models + initial migration applied successfully.
- One crawl run can be created and stored.
- One audit run can be generated from crawl pages.
- One markdown report can be generated and retrieved.
- Pipeline can be triggered via API (sync or queued MVP acceptable).
- Baseline tests exist and pass.
- `AGENT_HANDOFF.md` updated with run instructions, known issues, and next tasks.
- Commit created locally (no push unless explicitly authorized).

## 11. Exact Prompt to Give MiniMax Next
You are MiniMax implementation agent for MTVSEO. Work from branch `work` for now, but first configure/check `origin` and fetch all branches. If `main/master/dev/chore/stabilize-runtime` exist remotely, document differences and confirm the canonical base before feature work.

Complete tasks in this order:
1. MM-001 through MM-005 (branch/runtime/backend+DB baseline).
2. MM-006 through MM-010 (crawl→audit→report functional pipeline).
3. MM-011 (queue worker baseline) only after pipeline tests pass.
4. MM-012 and MM-013 (dashboard integration + approval gate).

Do not touch yet:
- Autonomous publishing.
- Paid/heavy integrations beyond initial PageSpeed stub.
- Advanced orchestration/multi-tenant auth/major UI redesign.

Validation requirements after each task batch:
- Run relevant pytest subsets.
- Run `python -m compileall services/api`.
- Run API startup smoke test.
- If frontend exists, run `npm run build`.
- Stop immediately and report root cause if validation fails; do not continue stacking changes on red state.

Commit discipline:
- Small, focused commits per task or small task batch.
- Commit message format: `feat(scope): summary` or `chore(scope): summary`.
- No push unless explicitly authorized.

Update `AGENT_HANDOFF.md` at end with:
- What was completed.
- Validation command outputs.
- Known blockers and exact next task ID.
