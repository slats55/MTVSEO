# Task Board — Autonomous SEO Agent OS

## Current Phase
**Phase 2A** — Stabilization, verification, local-dev reliability, and integration prep.

## Active Branches
- `master`: original starting point, last stable-ish
- `chore/stabilize-runtime`: stabilization commits (2 ahead of master) — **NOT YET MERGED**
- `feature/backend-phase2`: expanded backend smoke coverage, local dev runner — CURRENT BASE
- `chore/stepflash-project-audit`: Step Flash audit branch (this document lives here)

## Done (verified)
- [x] Project skeleton created (all packages and folders)
- [x] Database schema designed (20 entities) and Alembic initialized
- [x] FastAPI routers scaffolded (businesses, websites, crawls, pages)
- [x] Crawler package complete (robots, sitemap, page_fetcher, BFS runner, CLI worker)
- [x] SEO audit package complete (8 analyzers, scorer, reporter, CLI)
- [x] GEO audit package complete (5 analyzers, scorer, reporter, CLI)
- [x] Reporting package complete (Markdown formatter, generators)
- [x] Content engine package complete (brief generator, clusterer, planner, CLI)
- [x] Schema engine package complete (6 generators, validator, CLI)
- [x] Dashboard MVP scaffolded (Next.js 14, pages for businesses/audits/reports)
- [x] `.env.example` created with comprehensive placeholders
- [x] Backend smoke tests added (`tests/test_backend_smoke.py`)
- [x] Local verification script (`scripts/verify_local.py`)
- [x] Package renames fixed (hyphen → underscore) for Python import compatibility

## In Progress
- [ ] Backend runtime verification under Python 3.11+ (BLOCKED by environment)
- [ ] Frontend build verification (pending backend fix)
- [ ] Alembic migration verification (pending Python 3.11+)
- [ ] SQLite fallback test run (pending Python 3.11+)
- [ ] Documentation gap fill (9 missing docs)

## Blocked
- [ ] Python runtime — system Python 3.9.6 cannot import codebase; requires Python 3.11+
- [ ] Any `pytest` or `verify_local.py` execution until Python 3.11+ is available
- [ ] Frontend build not attempted (backend must import first for API integration planning)

## Next Up (ranked)
1. **Install Python 3.11+** and recreate virtualenv. This is the critical path.
2. Run `scripts/verify_local.py` and fix any import/runtime issues (likely none if Python version correct).
3. Run `pytest tests/ -q` and achieve green suite.
4. Test `alembic upgrade head` (from `services/api`) with SQLite fallback.
5. Run `tests/test_sqlite_fallback.py` to confirm local-dev DB path works without Postgres.
6. Build frontend: `cd apps/web && npm install && npm run build`. Fix TypeScript errors if any.
7. Update `.flash-task.txt` to current Step Flash task (it still says "create skeleton").
8. Create missing documentation (see Priority Docs below).
9. Expand smoke tests to cover at least one router endpoint and DB session.
10. Update `AGENT_HANDOFF.md` with Step Flash audit results before ending.

### Priority Documentation (missing)
- `docs/API_SPEC.md` — document all FastAPI endpoints with request/response examples
- `docs/AGENT_ROLES.md` — detailed 10-agent descriptions (currently only in AGENT_HANDOFF.md summary)
- `docs/ROADMAP.md` — phased timeline with milestone definitions
- `docs/DECISIONS.md` — architectural decision log (should reference ARCHITECTURE.md choices)
- `docs/CONTENT_WORKFLOW.md` — content brief → draft → review → publish flow
- `docs/PUBLISHING_SAFETY.md` — approval mode, rollback procedures, human-in-the-loop enforcement
- `docs/COMPLIANCE_GUARDRAILS.md` — detailed YMYL/cannabis rules, fake content禁止
- `docs/SEO_AUDIT_SCORING.md` — technical SEO score model formula and thresholds
- `docs/GEO_AUDIT_SCORING.md` — GEO score model formula and thresholds

Note: Many scoring details already exist in AGENT_HANDOFF.md and package READMEs; the missing docs should reference/consolidate rather than rewrite.

## Agent Division of Labor
- **MiniMax / Hermes (backend-heavy):** integrations (GSC, GA4, PageSpeed), Celery task wiring, LLM routing implementation, advanced SEO/GEO features.
- **Step Flash (verification/docs):** runtime stability, test expansion, documentation completion, small safe fixes, branch hygiene, handoff updates.
- **ChatGPT / User (product/approval):** direction decisions, merge approvals, review of architecture changes, content policies.

## Notes
- Do NOT merge `chore/stabilize-runtime` or `feature/backend-phase2` without explicit user instruction.
- Do NOT push to GitHub without explicit approval.
- Keep changes small, testable, and commit-ready.
- The project is in a **verification hole** due to Python version mismatch; that must be resolved first.
