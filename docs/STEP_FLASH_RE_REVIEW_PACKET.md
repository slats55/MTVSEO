# Step Flash Re-Review Packet

## When to Run This
Run this only after:
- Ryzen 9 MiniMax reports CRUD stabilization complete.
- Home PC Ryzen 7 MiniMax reports API contract audit complete.
- Both branches are pushed to origin.

## Branches to Review
- Base: `origin/feature/backend-phase2`
- Ryzen fixed branch: `origin/sync/ryzen9-minimax-latest`
- Home PC audit branch: `origin/review/homepc-api-contract-audit`
- Step Flash coordination branch: `origin/review/stepflash-merge-coordination-plan`

## Required Fetch
```bash
git fetch --all --prune
```

## Ryzen Re-Review Commands
```bash
# Inspect what changed since base
git log --oneline origin/feature/backend-phase2..origin/sync/ryzen9-minimax-latest
git diff --stat origin/feature/backend-phase2..origin/sync/ryzen9-minimax-latest
git diff --name-status origin/feature/backend-phase2..origin/sync/ryzen9-minimax-latest

# Create a review branch from their work and test
git switch -c review/stepflash-ryzen9-final-review origin/sync/ryzen9-minimax-latest

# Verify
python scripts/verify_local.py
pytest tests/test_endpoint_crud.py -q
pytest tests/ -q
python -m compileall services packages apps scripts tests
```

## Home PC Audit Review Commands
```bash
# Inspect audit document changes
git log --oneline origin/feature/backend-phase2..origin/review/homepc-api-contract-audit
git diff --stat origin/feature/backend-phase2..origin/review/homepc-api-contract-audit
git diff --name-status origin/feature/backend-phase2..origin/review/homepc-api-contract-audit
```

If the audit branch is absent, wait for Home PC to push it.

## Final Gate Checklist
Before recommending merge:
- [ ] CRUD tests pass (`pytest tests/test_endpoint_crud.py -q` green).
- [ ] Full pytest suite passes (`pytest tests/ -q` green).
- [ ] `compileall` passes.
- [ ] `scripts/verify_local.py` passes if present.
- [ ] No broad `pytest.mark.skip` added to hide failures.
- [ ] No accidental debug artifacts committed.
- [ ] `tests/uvicorn_server_test.py` remains untracked unless explicitly approved.
- [ ] Router response schemas match endpoint behavior (FastAPI response_model correctness).
- [ ] Website and crawl tests match actual API contracts.
- [ ] `db.refresh()` removal verified safe (responses still include generated IDs).
- [ ] `crawls.py` unreachable logger is fixed.
- [ ] GSC docs are either intentionally kept, moved to a dedicated folder, or excluded from merge.
- [ ] `sync/homepc-minimax-latest` is ignored as duplicate/incorrect branch.
- [ ] No force-push or branch deletion occurred.
- [ ] `AGENT_HANDOFF.md` updated if implementation changes affect coordination.

## Final Report Template
```markdown
Step Flash Final Re-Review Complete

Branches:
- Base: origin/feature/backend-phase2 (0fb1772)
- Ryzen branch: origin/sync/ryzen9-minimax-latest (commit)
- Home PC audit branch: origin/review/homepc-api-contract-audit (commit)
- Local final review branch: review/stepflash-ryzen9-final-review

Verification:
- verify_local.py: [PASS/FAIL] [notes]
- pytest tests/test_endpoint_crud.py -q: [summary]
- pytest tests/ -q: [summary]
- compileall: [PASS/FAIL]

Ryzen findings:
- CRUD tests: [pass/fail, known failures]
- Router changes: [db.refresh removal impact assessment]
- Schema alignment: [do responses match schemas?]
- Remaining risks: [any]

Home PC audit findings:
- Useful findings: [list]
- Conflicts with Ryzen: [any]
- Contract conclusions: [API contract upheld?]

Merge recommendation:
- Merge Ryzen into feature/backend-phase2 now? Yes/No
- Merge Home PC audit doc now? Yes/No
- Exclude any docs? Yes/No
- Remaining blockers: [list]
```

## After Re-Review
If both branches are green:
1. Prepare a final summary for the user.
2. Do not merge yourself; recommend merge and wait for approval.
3. Update `AGENT_HANDOFF.md` to reflect the upcoming merge and any follow-up tasks.
