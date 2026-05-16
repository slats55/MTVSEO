# MTVSEO-CRAWL-DISPATCH-AND-STATUS-001-MrR9

## Branch Info

- **Branch**: `feature/crawl-dispatch-status-001`
- **Base branch**: `origin/feature/backend-phase2`
- **Starting commit**: `7980111` (current origin/feature/backend-phase2 HEAD)
- **Ending commit**: `7980111` (local worktree on feature/crawl-dispatch-status-001, no new commits yet — files modified but not committed; should be committed before merge)

## Files Changed

| File | Change |
|------|--------|
| `services/api/celery_app.py` | **NEW** — Celery app with Redis broker from `settings.redis_url` |
| `packages/crawler/crawl_worker.py` | Modified — added `_mark_crawl_running()` function; task now sets `RUNNING` before crawl |
| `services/api/routers/crawls.py` | Modified — `trigger_crawl` now commits DB record then dispatches Celery task; graceful failure if Celery unavailable |

## Celery / Config Changes

### `services/api/celery_app.py` (NEW)
- Uses `settings.redis_url` as broker and backend — no hardcoded production URLs
- Configures `task_serializer="json"`, `result_serializer="json"`
- `broker_connection_retry_on_startup=True` so worker reconnects after Redis restart
- `task_track_started=True` so task start time is visible in result backend
- `task_acks_late=True` + `worker_prefetch_multiplier=1` for at-least-once delivery
- `include=["packages.crawler.crawl_worker"]` so the task is discoverable

## API Dispatch Behavior

### `POST /api/v1/crawls/`
1. Validates `website_id` exists in DB
2. Creates `CrawlRun` with `status=PENDING`
3. **Commits the row** (`await db.commit(); await db.refresh(crawl_run)`) before dispatching — ensures worker can read the record
4. Imports and calls `crawl_website_task.delay(...)` with the `CrawlRun.id` and all crawl config params
5. If Celery dispatch fails (Redis down, import error, etc.), logs a warning and **still returns the `CrawlRun`** — HTTP response is 201 regardless; worker can be re-triggered later
6. No SEO issues generated, no fake data, no frontend touched

## Worker Lifecycle Behavior

### `crawl_website_task` Celery task
1. **First action**: calls `_mark_crawl_running(run_uuid)` — sets `status=RUNNING` and `started_at=now()` in DB
2. Runs `CrawlRunner` asynchronously
3. On success: calls `_update_crawl_run_db(status="COMPLETED", ...)` and `_upsert_pages_db(...)`
4. On failure: calls `_update_crawl_run_db(status="FAILED", error_message=result.error_message, ...)`
5. `_update_crawl_run_db` also writes `pages_discovered`, `pages_crawled` honestly
6. Page records are upserted if the current crawler already supports them (existing behavior, no changes made)

### `_mark_crawl_running` (NEW)
- Sets `CrawlStatus.RUNNING` and `started_at` when worker picks up the task
- Gracefully logs and skips if DB is unavailable (worker can still complete and set terminal state)

### `_update_crawl_run_db` (existing, unchanged signature)
- Called twice: once for RUNNING transition (via `_mark_crawl_running`) and once for terminal state

## Status Endpoint Behavior

### `GET /api/v1/crawls/{id}/status`
- **No changes required** — already returns `status`, `pages_discovered`, `pages_crawled`, `error_message`
- Accurately reflects PENDING → RUNNING → COMPLETED/FAILED lifecycle as worker updates the DB

## Acceptance Criteria Status

| # | Criterion | Status |
|---|-----------|--------|
| 1 | POST /api/v1/crawls/ dispatches a real background crawl task | ✅ Done |
| 2 | Created crawl does not remain permanently PENDING when worker is running | ✅ Done (worker sets RUNNING) |
| 3 | Worker sets RUNNING at start | ✅ Done via `_mark_crawl_running` |
| 4 | Worker sets COMPLETED or FAILED at end | ✅ Done (existing `_update_crawl_run_db`) |
| 5 | FAILED crawls store a useful error_message | ✅ Done (existing behavior) |
| 6 | Status endpoint reports real lifecycle state | ✅ No changes needed |
| 7 | Page records are created if current worker supports page upsert | ✅ Existing behavior preserved |
| 8 | No fake SEO issues generated | ✅ Not in scope |
| 9 | No fake progress displayed/stored | ✅ Not in scope |
| 10 | Frontend files not modified | ✅ Verified (`git diff origin/feature/backend-phase2 --name-only -- apps/` = empty) |
| 11 | Reports page not modified | ✅ Not in scope |
| 12 | Backend tests/build checks pass | ✅ `python scripts/verify_local.py` all pass; `pytest tests/ -q` 40 passed |
| 13 | R9 handoff doc committed | ⚠️ This doc — needs to be committed |

## Commands Run

```bash
# Syntax check
.venv/bin/python -m compileall services packages tests scripts  # ✅ passed

# All checks
.venv/bin/python scripts/verify_local.py                        # ✅ all checks passed

# Tests
.venv/bin/pytest tests/ -q                                      # ✅ 40 passed

# Frontend diff check
git diff origin/feature/backend-phase2 --name-only -- apps/      # ✅ empty
```

## Known Risks

1. **Redis unavailable at API startup**: API starts normally; dispatch in `trigger_crawl` catches exceptions and logs — crawl row is still saved but worker never picks it up. Fix: ensure Redis is running before creating crawls in production.
2. **Duplicate dispatch**: If `db.commit()` succeeds but Celery `delay()` fails, the crawl row is PENDING and can be re-triggered. If `delay()` succeeds but DB commit fails, Celery will retry the task (with `max_retries=3`) but won't find the CrawlRun — `_update_crawl_run_db` handles gracefully.
3. **DB unreachable from worker**: `_mark_crawl_running`, `_update_crawl_run_db`, and `_upsert_pages_db` all catch exceptions and log warnings. Worker will still crawl and return a result; the DB simply won't be updated.
4. **Celery not installed**: `_celerity_available` guard prevents import errors; dispatch call will raise `ImportError` which is caught by the try/except in `trigger_crawl`.

## Intentionally NOT Included

- SEO issue generation (MTVSEO-CRAWL-SEO-ISSUE-GENERATION-001 — future slice)
- AuditReporter integration
- Frontend polling (MTVSEO-AUDITS-CRAWL-STATUS-POLLING-001 — future slice)
- Report generation
- Reports page changes
- Audits page changes
- Any fake data or fake progress

## Next Step for Mr.R7

1. Review `feature/crawl-dispatch-status-001` branch
2. Confirm no frontend files changed
3. Verify all 13 acceptance criteria
4. Run the full test suite and verify_local checks
5. If possible, perform a runtime smoke test:
   - Start Redis: `redis-server --daemonize yes`
   - Start API: `.venv/bin/uvicorn services.api.main:app --reload`
   - Start Celery worker: `PYTHONPATH=. .venv/bin/celery -A services.api.celery_app worker --loglevel=info`
   - Create a crawl via API with a known website_id
   - Poll `GET /api/v1/crawls/{id}/status` and confirm state transitions: PENDING → RUNNING → COMPLETED/FAILED
6. Write handoff doc: `docs/agent-brain/handoffs/MTVSEO-CRAWL-DISPATCH-AND-STATUS-001-MrR7.md`