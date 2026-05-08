# Step Flash CRUD Review Runbook

## Purpose
This document prepares the review process for Ryzen 9's CRUD/API implementation branch. It defines the stable base, review scope, exact commands to run, pass/failure criteria, and the final report template. The goal is to enable fast, safe, and consistent review once the implementation is pushed.

## Stable Base

- **Base branch**: `feature/backend-phase2`
- **Base commit**: `0fb1772` — "docs: add Phase 2 documentation foundation"
- **Current verification status**: ✅ PASS
  - `python scripts/verify_local.py` — all checks passed
  - `pytest tests/ -q` — 22 tests passed
  - `python -m compileall services packages tests` — no errors
  - FastAPI app imports cleanly
  - Health endpoint returns 200
  - DB config uses SQLite fallback acceptable for local dev

## Incoming Branch To Review Later

- `origin/sync/ryzen9-minimax-latest`

## Review Scope

Focus strictly on the CRUD/API implementation. Do not consider unrelated changes.

- `tests/test_endpoint_crud.py` — primary test file
- `services/api/routers/businesses.py` — business CRUD endpoints
- `services/api/routers/websites.py` — website CRUD endpoints
- `services/api/routers/crawls.py` — crawl CRUD endpoints
- `services/api/models/` — SQLAlchemy models alignment with schemas
- `services/api/schemas/` — Pydantic request/response schemas
- `services/api/database.py` — session lifecycle, async behavior
- `services/api/main.py` — router registration, startup/shutdown hooks

Specific concerns:
- `await db.refresh()` removal from CRUD return paths (should return model_copy())
- Placeholder user behavior (whoami / default user handling)
- Response model correctness (status_code, response_model, 201 vs 200)
- List vs Get vs Create API contract consistency
- SQLite test compatibility (aiosqlite, uri=True)
- No hardcoded test-only hacks leaking into production
- No weakened tests or implementation shortcuts

## Commands To Run Once Ryzen 9 Pushes

```bash
# From repo root
git fetch origin

# Show what changed relative to base
git log --oneline feature/backend-phase2..origin/sync/ryzen9-minimax-latest
git diff feature/backend-phase2..origin/sync/ryzen9-minimax-latest --stat
git diff feature/backend-phase2..origin/sync/ryzen9-minimax-latest

# Create local review branch tracking the incoming branch
git checkout -B local-review-ryzen9-crud origin/sync/ryzen9-minimax-latest

# Activate venv
source .venv/bin/activate
export PYTHONPATH=.

# Verify local environment
python scripts/verify_local.py

# Run CRUD tests first (the critical path)
pytest tests/test_endpoint_crud.py -q

# Run full test suite
pytest tests/ -q

# Compileall check
python -m compileall services packages tests

# Optional: import sanity
python -c "from services.api.main import app; print('FastAPI OK')"
```

## Pass Criteria

All must be true:

- CRUD test file (`tests/test_endpoint_crud.py`) passes without xfails or skips
- Full test suite passes (no regressions; 22+ tests remain green)
- `compileall` passes (no syntax errors)
- FastAPI app imports cleanly
- No implementation shortcuts:
  - No `await db.refresh()` in endpoint returns
  - No test-only conditionals (e.g., `if TESTING: ...`)
  - No hardcoded IDs or mock objects in production code
- No weakened tests (tests should assert real behavior, not stubs)
- No unrelated rewrites (no large refactors outside the CRUD scope)
- No broken base behavior (health endpoint, other existing endpoints unaffected)
- No frontend or documentation noise (focus is backend CRUD only)
- API response contracts consistent across list/get/create

## Failure Criteria (Block Merge)

Any one of these blocks merge:

- CRUD tests still fail (errors or assertion failures)
- Full test suite regresses (previous tests now fail)
- Schema/model mismatch remains (Pydantic vs SQLAlchemy misalignment)
- Database/session lifecycle is unsafe (missing commit/rollback, session leaks)
- Hardcoded test-only hacks are present in production code
- Unrelated changes dominate the diff (e.g., massive formatting rewrites)
- Uncommitted changes on review branch
- Implementation branch not pushed to remote (cannot verify CI/CD)

## Final Review Report Template

After running the verification, fill in and publish to the chat:

```
=== Step Flash CRUD Review ===
Branch reviewed: origin/sync/ryzen9-minimax-latest
Base: feature/backend-phase2 @ 0fb1772

Commands run:
- verify_local.py: [PASS/FAIL]
- pytest tests/test_endpoint_crud.py: [PASS/FAIL]
- pytest tests/ (full): [PASS/FAIL]
- compileall: [PASS/FAIL]
- FastAPI import: [PASS/FAIL]

Changes observed:
- Files modified: N
- Lines added/removed: +X -Y
- Key changes: [brief bullet list]

Issues found:
- [List each with severity and file/line if possible]

Pass criteria met: [YES/NO]
Failure criteria triggered: [YES/NO]

Merge recommendation: [YES/NO]
Notes: [free-form]
```

Do not edit any implementation code during the review. Only document findings.
