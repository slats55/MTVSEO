# Step Flash GSC Review Protocol

## Purpose

This checklist is used by Step Flash (MacBook gatekeeper) to review the MiniMax Google Search Console integration slice before it is pushed to GitHub and merged into `feature/backend-phase2`.

The reviewer MUST NOT implement new features or fix backend code. The reviewer's job is to verify, document, and gate-keep only.

## Branch Strategy

- **Base branch:** `feature/backend-phase2` (stable, verified, fully documented)
- **Implementation branch:** `feature/gsc-integration-slice` (MiniMax work)
- **Review branch:** `qa/stepflash-gsc-review-protocol` (this protocol lives here; do not merge)

After review and approval:
1. MiniMax pushes `feature/gsc-integration-slice`
2. Step Flash merges into `feature/backend-phase2` locally
3. Step Flash runs final verification
4. Step Flash pushes `feature/backend-phase2`
5. Step Flash updates `AGENT_HANDOFF.md` and `docs/TASK_BOARD.md`

## Pre-Review Setup

```bash
# Ensure base is fresh
git fetch origin --all --prune
git checkout feature/backend-phase2
git pull origin feature/backend-phase2
git log --oneline --decorate -n 10

# Switch to implementation branch
git checkout feature/gsc-integration-slice
git pull origin feature/gsc-integration-slice

# Show diff summary
git diff --stat feature/backend-phase2...feature/gsc-integration-slice
```

## Review Checklist

### A. Scope Guardrails

- [ ] No frontend dashboard wiring changes unless explicitly scoped
- [ ] No auto-publishing endpoints added
- [ ] No AI content generation endpoints added
- [ ] No Celery/RQ worker implementation (unless explicitly in slice)
- [ ] No database redesign beyond planned `Audit` and `ContentPlan` tables
- [ ] No auth/authentication system added
- [ ] No fake data, fake claims, or fake business stats anywhere in code or docs

### B. Code Changes Review

List all changed files:

```bash
git diff --name-only feature/backend-phase2...feature/gsc-integration-slice
```

For each changed file:

- [ ] Backend Python files: check import correctness, type hints, no circular imports
- [ ] New packages: verify `__init__.py` exists and exports are clean
- [ ] Database models: confirm foreign keys, indexes, Alembic autogenerate will detect changes
- [ ] API routers: check route definitions, response models, status codes, error handling
- [ ] Config changes: `.env.example` updated with GSC-specific keys only (no secrets)
- [ ] No hardcoded credentials or API keys anywhere
- [ ] No `print()` debugging left in (use proper logging)
- [ ] No commented-out code blocks that should be deleted

### C. Tests

Run full test suite:

```bash
source .venv/bin/activate
PYTHONPATH=. python -m pytest tests/ -q
```

- [ ] All existing 22 tests still pass
- [ ] New tests added for GSC integration:
  - [ ] At least one API endpoint test (mock GSC client)
  - [ ] Integration test for token fetch/refresh (if applicable)
  - [ ] SQLite fallback still works with new code paths
  - [ ] No test relies on live network calls (use fixtures/mocks)

Run compileall:

```bash
PYTHONPATH=. python -m compileall services packages scripts tests
```

- [ ] No compilation errors

### D. FastAPI Import & Runtime

```bash
PYTHONPATH=. python -c "from services.api.main import app; print('OK')"
```

- [ ] App imports without errors
- [ ] No Pydantic configuration warnings

### E. Documentation Updates

Check that the following were updated (if applicable):

- [ ] `docs/API_SPEC.md` — new GSC endpoints documented with request/response examples
- [ ] `docs/AGENT_ROLES.md` — Integrations Agent role remains accurate; no new roles added
- [ ] `docs/ROADMAP.md` — Phase 9 (Integrations) milestone adjusted to show GSC as first slice
- [ ] `docs/DECISIONS.md` — new architectural decisions recorded with rationale
- [ ] `AGENT_HANDOFF.md` — Appendix or new section added describing GSC slice scope and decisions
- [ ] `docs/TASK_BOARD.md` — Next Up items adjusted; GSC integration moved from "planned" to "in progress" or "done"
- [ ] `.env.example` — new GSC variables added with safe placeholder values
- [ ] No existing docs were overwritten with incomplete/placeholder content

### F. Compliance & Safety

- [ ] No fake search console data or fabricated metrics
- [ ] No auto-publishing to Google Search Console (draft-only or explicit human action required)
- [ ] API key handling uses environment variables only
- [ ] Error messages are user-friendly and do not leak internals
- [ ] Rate limiting considerations documented (even if not implemented yet)

### G. Frontend Impact

If `apps/web/` was modified:

- [ ] `npm run build` succeeds
- [ ] No new runtime errors in Next.js build
- [ ] New pages/components have proper TypeScript types
- [ ] No broken internal links in navigation

If `apps/web/` was NOT modified:
- [ ] Confirm build still passes (regression check)

### H. Database & Migrations

- [ ] If new models added: Alembic migration generated and applies cleanly
- [ ] Migration file follows naming convention (`xxxx_name.py`)
- [ ] Migration tested with SQLite fallback: `alembic upgrade head` runs without errors
- [ ] No destructive operations (column drops) without explicit reviewer approval

### I. Git hygiene

- [ ] Commits are small and focused (no giant "everything" commit)
- [ ] Commit messages follow conventional format (`feat:`, `fix:`, `docs:`, `test:`)
- [ ] No merge commits in the feature branch
- [ ] No `.env` secrets committed (only `.env.example`)
- [ ] No IDE/editor config files (.vscode, .idea) added
- [ ] No build artifacts in commits (`node_modules/`, `.next/`, `__pycache__/`)

### J. Conflict Readiness

Anticipate merge conflicts:

- [ ] `docs/TASK_BOARD.md` — may need manual merge combining Step Flash's existing content with GSC progress notes
- [ ] `AGENT_HANDOFF.md` — may need merge combining handoff sections
- [ ] `.env.example` — if both branches modified, preserve ALL keys (GSC + existing) in alphabetical/section order
- [ ] `pyproject.toml` or `requirements.txt` — if new deps added, ensure versions pinned or compatible

## Post-Merge Verification (after merging into feature/backend-phase2)

```bash
# On feature/backend-phase2 after merge
git status
git log --oneline -n 5
```

Run full suite again:

```bash
source .venv/bin/activate
PYTHONPATH=. python scripts/verify_local.py
PYTHONPATH=. python -m pytest tests/ -q
PYTHONPATH=. python -m compileall services packages scripts tests
cd apps/web && npm run build && cd ../..
```

- [ ] All checks still pass
- [ ] No new warnings or errors introduced

## Final Sign-Off

After successful review:

1. Notify MiniMax that the branch passed Step Flash review
2. Wait for explicit user approval before merging to `feature/backend-phase2`
3. After merge, update `AGENT_HANDOFF.md` with a new section:

```markdown
## GSC Integration Slice — Merged YYYY-MM-DD

- Branch: feature/gsc-integration-slice
- Files changed: [list from git diff --stat]
- Tests added: [count and brief description]
- Docs updated: [list]
- Verification: all green
- Next: [remaining work for Phase 2B]
```

4. Update `docs/TASK_BOARD.md`:
   - Move "GSC integration" from Next Up to Done
   - Add any new Next Up items created by this slice (e.g., "GA4 integration slice", "PageSpeed integration slice")

## Blockers — When to Halt

Stop the review and report immediately if:

- [ ] Any existing test fails (22 baseline must stay green)
- [ ] FastAPI import fails
- [ ] Frontend build breaks
- [ ] Fake data or black-hat SEO tactics found in code/comments
- [ ] Auto-publishing or human-safety bypass discovered
- [ ] Secrets or real API keys committed
- [ ] Large refactoring outside GSC scope (e.g., rewriting crawler, changing DB engine)

## Non-Goals for This Review

- Do NOT review business logic correctness of GSC API parsing (assume MiniMax owns feature correctness)
- Do NOT optimize performance or add caching unless explicitly part of slice
- Do NOT add new integrations (GA4, PageSpeed) unless explicitly in this branch
- Do NOT merge to main/master ever

---

*Protocol version:* 1.0  
*Created:* 2025-05-08  
*Branch:* `qa/stepflash-gsc-review-protocol`  
*Base:* `feature/backend-phase2` commit `0fb1772`
