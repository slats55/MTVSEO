# Local Verification Runbook

## Purpose

This runbook standardizes how Ryzen 9 MiniMax, Home PC MiniMax, and Step Flash should verify backend changes before merge. It ensures consistent commands, environment setup, and pass/fail gates across all three agents regardless of host OS or local configuration quirks.

---

## Known Environment Differences

| Issue | Home PC (Atsuko) | Ryzen 9 (prior report) | Workaround |
|---|---|---|---|
| pytest missing | Was missing, now installed in `.venv` | Reported missing initially | Always activate `.venv` before running pytest |
| verify_local.py execution | Present, runs cleanly with `.venv` python | May not have been present | Check `scripts/verify_local.py` exists before running |
| compileall timeout | Times out at 60s when run through short-timeout wrappers | Same | Run compileall with explicit timeout >= 120s; it passes on this machine |
| WSL `/mnt/c` path | `/mnt/c/Users/mtval/Projects/seo-agent-os` | Likely similar | Always use absolute paths; don't rely on cwd being set correctly |
| Node.js version | v22.22.2 | Unknown | Documented for reference |
| npm version | 10.9.7 | Unknown | Documented for reference |
| Python system python | Python 3.12.3 (system `/usr/bin/python3.12`) | Unknown | Use `.venv/bin/python3.12` for all repo work, not system python |

---

## Recommended Python Environment Setup

### Step 1 — Identify your Python

```bash
# Check what's available
python3.12 --version   # most likely available on Linux/WSL
python3.11 --version
python --version
```

### Step 2 — Create a fresh virtual environment

```bash
# From repo root — Linux/WSL
rm -rf .venv
python3.12 -m venv .venv

# From repo root — Windows PowerShell (if using Git Bash or WSL)
rm -rf .venv
python -m venv .venv
```

### Step 3 — Activate the environment

```bash
# Linux/WSL (bash/zsh)
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat
```

### Step 4 — Install dependencies

```bash
# Install all backend dependencies (includes dev deps via requirements-dev.txt)
pip install -r requirements-dev.txt

# If requirements-dev.txt is missing or incomplete, fall back to:
pip install -r requirements.txt
pip install pytest pytest-asyncio aiosqlite ruff mypy
```

### Step 5 — Verify the environment

```bash
# Should show Python 3.11+ and pytest installed
python --version
.venv/bin/pytest --version
```

### Environment files found in this repo

- `requirements.txt` — backend production dependencies (fastapi, sqlalchemy, pydantic, etc.)
- `requirements-dev.txt` — dev dependencies; includes `-r requirements.txt` so one install gets everything
- `pyproject.toml` — package metadata; does not contain pip-installable dependencies
- `apps/web/package.json` — Next.js frontend; not needed for backend verification

---

## Standard Backend Verification Commands

### Full verification (all-in-one)

```bash
PYTHONPATH=. .venv/bin/python scripts/verify_local.py
```

This runs 7 checks: Python version, dependency imports, package imports, package exports, FastAPI app import, health endpoint, DB config. All must pass.

**Expected output**: `✓ ALL CHECKS PASSED`

---

### Run all tests

```bash
PYTHONPATH=. .venv/bin/pytest tests/ -q
```

Runs all tests excluding endpoint_crud (22 tests on base). Must pass before any branch is considered merge-ready.

**Expected output**: `22 passed` or similar

---

### Run only CRUD endpoint tests (the ones Ryzen is fixing)

```bash
PYTHONPATH=. .venv/bin/pytest tests/test_endpoint_crud.py -q
```

On the base branch, these should pass (12 tests). On `origin/sync/ryzen9-minimax-latest`, 9 currently fail due to a missing `text` import in the test file — this is the primary target for Ryzen's fix.

**Expected output after fix**: `12 passed`

---

### Run tests excluding CRUD (useful when CRUD is known-broken)

```bash
PYTHONPATH=. .venv/bin/pytest tests/ -q -k "not endpoint_crud"
```

**Expected output**: `22 passed`

---

### Syntax/compilation check

```bash
PYTHONPATH=. .venv/bin/python -m compileall services packages apps scripts tests
```

Validates that all Python files compile without syntax errors. **Can take up to 2 minutes** — do not set a short timeout. On Home PC this passes cleanly.

**Expected output**: No errors. (Timed out in prior runs with short timeouts; allow 120–180s.)

---

### Single command to run all backend gates

```bash
PYTHONPATH=. .venv/bin/python scripts/verify_local.py && \
PYTHONPATH=. .venv/bin/pytest tests/ -q && \
PYTHONPATH=. .venv/bin/pytest tests/test_endpoint_crud.py -q
```

All three must exit 0.

---

## Frontend Verification Commands

Frontend lives in `apps/web/` (Next.js 14). Backend verification does NOT require frontend to be built. However, if you've made frontend changes:

```bash
# From repo root — install frontend dependencies
cd apps/web
npm install

# Build to verify no TypeScript / build errors
npm run build
```

**When to run frontend checks:**
- Only if you've edited files in `apps/web/`
- Not required for backend-only changes
- Not required for router, schema, or test changes

---

## Troubleshooting

### pytest not found

```bash
# Check if it's in the venv
ls .venv/bin/pytest
.venv/bin/pytest --version

# If missing, install
pip install pytest pytest-asyncio

# Or via requirements-dev.txt
pip install -r requirements-dev.txt
```

### verify_local.py not found

```bash
# Check it exists
ls scripts/verify_local.py

# If missing, the script may not have been created yet
# This is expected on some older branches
# Skip verify_local.py and use pytest + compileall instead
```

### compileall timeout

```bash
# Run with explicit high timeout
PYTHONPATH=. timeout 180 .venv/bin/python -m compileall services packages apps scripts tests

# If it still times out, check for circular imports or very large files
# A timeout here does NOT block merge — document it and proceed
```

### SQLite UUID issues

The tests use in-memory SQLite (`sqlite+aiosqlite:///file::memory:`). UUIDs are stored as TEXT in SQLite. The test fixtures handle this correctly. If you see UUID comparison failures:
- Tests use `uuid.UUID(data["id"])` and `str(uuid.UUID(...))` to normalize
- This pattern is correct and should not be changed

### WSL /mnt/c filesystem slowness

The repo is cloned at `/mnt/c/Users/mtval/Projects/seo-agent-os` (Windows-mounted filesystem). File operations are slower than native Linux. Effects:
- `compileall` can take 2+ minutes
- pip installs may be slower
- Do not use tight timeouts (< 60s) for compileall or pip operations

### npm install problems on Windows-mounted filesystem

WSL + `/mnt/c` + `npm install` can be very slow or fail due to symlink permission issues.

```bash
# If npm install fails on /mnt/c:
# Option 1: Run from native Windows PowerShell
cd C:\Users\mval\Projects\seo-agent-os\apps\web
npm install

# Option 2: Accept that npm install on /mnt/c may be slow
# Frontend verification is not blocking for backend PRs
```

### Missing `text` import in test_endpoint_crud.py (the current Ryzen fix target)

If you see `NameError: name 'text' is not defined` in test output, the fix is:

```python
# In tests/test_endpoint_crud.py, add to imports:
from sqlalchemy import text
```

This is the primary issue blocking `origin/sync/ryzen9-minimax-latest` from passing all tests.

---

## Multi-Agent Verification Policy

### Implementation agent (Ryzen 9) must:
1. Run `pytest tests/test_endpoint_crud.py -q` first (targeted test)
2. Then run `pytest tests/ -q` (full suite)
3. Then run `PYTHONPATH=. python scripts/verify_local.py`
4. Fix any failures before pushing or requesting review
5. Report which commands were run and their output in the PR description

### Reviewer agent (Step Flash / Home PC secondary) must:
1. Independently re-run all verification commands on the review branch
2. Not rely on the implementation agent's reported output
3. Verify `compileall` if time allows (can skip if timing out consistently)

### No branch should merge with:
- Known failing tests (unless explicitly marked WIP with tracked exclusions)
- `compileall` errors (syntax errors must be fixed)
- verify_local.py failures (dependency issues must be resolved)

### Do NOT:
- Hide failures with broad `pytest --ignore` or `-k "not"` skips (except for tracked WIP items)
- Force push shared branches (`sync/ryzen9-minimax-latest`, `sync/homepc-minimax-latest`)
- Merge to `main` or `feature/backend-phase2` without explicit coordination

---

## Current Recommended Gate for origin/sync/ryzen9-minimax-latest

Before Step Flash re-reviews, `origin/sync/ryzen9-minimax-latest` should pass:

```bash
# 1. CRUD tests — the primary fix target
PYTHONPATH=. .venv/bin/pytest tests/test_endpoint_crud.py -q
# Expected: 12 passed (after Ryzen's fix)

# 2. Full test suite — no regressions
PYTHONPATH=. .venv/bin/pytest tests/ -q
# Expected: 34 passed (22 non-CRUD + 12 CRUD after fix)

# 3. Environment verification
PYTHONPATH=. .venv/bin/python scripts/verify_local.py
# Expected: ✓ ALL CHECKS PASSED

# 4. Syntax check (allow 2+ min timeout)
PYTHONPATH=. .venv/bin/python -m compileall services packages apps scripts tests
# Expected: no errors
```

Current status (before Ryzen's fixes):
- `test_endpoint_crud.py`: 9 failed, 3 passed — root cause: missing `text` import
- `tests/ -q` (excluding endpoint_crud): 22 passed
- `verify_local.py`: ✓ ALL CHECKS PASSED
- `compileall`: previously confirmed passing (timed out on some runs due to `/mnt/c` slowness)

---

## Final Checklist

Copy and paste before reporting completion:

```bash
# === GATE 1: Environment ===
python3.12 --version          # Should be 3.11+
.venv/bin/python --version    # Should be 3.11+
.venv/bin/pytest --version    # Should show pytest 8+

# === GATE 2: CRUD tests (the fix target) ===
PYTHONPATH=. .venv/bin/pytest tests/test_endpoint_crud.py -q
# Must see: 12 passed

# === GATE 3: Full suite ===
PYTHONPATH=. .venv/bin/pytest tests/ -q
# Must see: 34 passed (or N passed, consistent with baseline)

# === GATE 4: Verify script ===
PYTHONPATH=. .venv/bin/python scripts/verify_local.py
# Must see: ✓ ALL CHECKS PASSED

# === GATE 5: Syntax (allow 2+ min) ===
PYTHONPATH=. .venv/bin/python -m compileall services packages apps scripts tests
# Must exit 0

# === REPORT ===
echo "All gates passed on $(hostname) at $(date)"
```

If any gate fails, do not push or request review. Fix first.

---

## Environment Facts (as of this run on Home PC / Atsuko)

- Python system: `3.12.3` (WSL Debian, `/usr/bin/python3.12`)
- venv Python: `3.12.3` (`.venv/bin/python3.12`)
- pytest: `9.0.3`
- Node: `v22.22.2`
- npm: `10.9.7`
- repo root: `/mnt/c/Users/mtval/Projects/seo-agent-os`
- verify_local.py: present and passing
- requirements-dev.txt: present (includes `-r requirements.txt` + pytest + ruff)
- compileall: passes (allow 2 min)
- WSL `/mnt/c` path: confirmed working for all Python operations