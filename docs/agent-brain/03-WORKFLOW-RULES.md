# Workflow Rules

## Branch Discipline

1. **Use descriptive branch names** with prefixes:
   - `feat/` — new features
   - `fix/` — bug fixes
   - `docs/` — documentation only
   - `chore/` — maintenance, setup, tooling
   - `audit/` — review/audit tasks
   - `review/` — review preparation
   - `sync/` — syncing with remote
   - `qa/` — quality assurance

2. **Branch from the correct base**: Always branch from `feature/backend-phase2` unless explicitly directed otherwise.

3. **Keep branches focused**: One logical change per branch when possible.

4. **Sync before branching**: Run `git fetch --all --prune` before creating a new branch to ensure you have latest.

## Data Rules

1. **No fake/mock data unless explicitly approved** — Use real data or clearly documented seed data.
2. **No invented verification results** — Always run actual checks; do not report assumed results.
3. **No placeholder fixes** — If you don't know the fix, document the issue in `05-KNOWN-ISSUES.md` instead.

## Edit Ownership

1. **No overlapping edits without assigned ownership** — If two agents need to edit the same file, assign ownership to one agent.
2. **Handoff before taking over** — If you need someone else's file, ask for a handoff first.
3. **Agents must not overwrite another agent's handoff** — Handoff files in `handoffs/` are owned by the agent who created them.

## Task Handoff Rules

1. **Every task gets a handoff note** — When completing or handing off a task, write a handoff file in `docs/agent-brain/handoffs/`.
2. **Handoff naming**: `<TASK_ID>-<AGENT_ID>.md`
3. **Handoff must include**: task ID, branch, base branch, commit hash, files changed, commands run, verification results, blockers, next recommended action.

## Verification Rules

1. **Every implementation needs verification** — After making changes, run:
   - `python -m compileall .` (syntax check)
   - `python scripts/verify_local.py` (local verification if exists)
   - `pytest tests/ -q` (test suite if applicable)
2. **Report actual results** — Do not report assumed or hoped-for results.
3. **Blockers must be documented** — If verification fails, document in `05-KNOWN-ISSUES.md` before handing off.

## Review Rules

1. **Reviewers must block unsafe changes** — Mr.M1 and any reviewer must not approve changes that break tests, introduce security issues, or violate these rules.
2. **Step Flash review required** — Before merging implementation branches into `feature/backend-phase2`, a Step Flash review is required.
3. **No bypass of review** — Even small changes require review. Small ≠ exempt.

## General Safety Rules

1. **No destructive git commands** on main/feature branches without explicit approval
2. **No database wipe/reset commands** unless explicitly approved
3. **Docker commands**: Only safe inspection commands (`docker compose config`, `docker compose ps`, `docker compose logs`) unless explicitly approved
4. **Forbidden unless explicitly approved**:
   - `docker system prune -a`
   - `docker volume prune`
   - `docker compose down -v`
   - `rm -rf` (on repo files)
   - Database wipe/reset commands
   - Mass deletion commands

---

*Last updated by: Mr.R9 (setup task MULTICA-OBSIDIAN-BRAIN-SETUP-001)*