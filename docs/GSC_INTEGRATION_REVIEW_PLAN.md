# GSC Integration Review Plan — Phase 2B

**Status:** Ready for review
**Branch:** `review/phase2b-gsc-review-plan` (from `feature/backend-phase2`)
**For reviewing:** `feature/gsc-integration-slice` (being built by MiniMax on Ryzen 9 laptop)
**Created:** 2026-05-08

---

## Purpose

This document defines what the GSC integration slice must include, how it must be tested, and what risks to watch for. Use this as a checklist when MiniMax's `feature/gsc-integration-slice` branch is ready for review.

**Role:** Secondary Reviewer — do not implement, push, or merge. Only review, verify, and report.

---

## 1. Expected Files from the GSC Slice

The slice should add/modify files within `packages/integrations/`:

```
packages/integrations/
  __init__.py              # already exists (empty stub)
  README.md                # already exists
  gsc_client.py            # NEW — main GSC API client
  gsc_models.py            # NEW — Pydantic request/response models
  gsc_router.py            # NEW — FastAPI router with endpoints
  tests/
    test_gsc_client.py     # NEW — unit tests (mocked)
    test_gsc_router.py     # NEW — endpoint smoke tests
```

**Acceptance:** At minimum, `gsc_client.py` and `tests/test_gsc_client.py` must exist. `gsc_router.py` is expected for Phase 2B but may be deferred to Phase 2C.

---

## 2. Expected Public Interface (GscClient)

```python
class GscClient:
    """Google Search Console API client."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        token_store: GscTokenStore | None = None,
    )
    
    async def get_authorization_url(state: str) -> str
    async def exchange_code(code: str) -> GscTokens
    async def refresh_token_if_needed() -> None
    async def list_sites() -> list[GscSiteEntry]
    async def get_search_analytics(
        site_url: str,
        start_date: date,
        end_date: date,
        dimensions: list[str] | None = None,
        row_limit: int = 1000,
    ) -> GscSearchAnalyticsResponse
    async def close() -> None
```

**Acceptance:** GscClient must be importable from `packages.integrations.gsc_client`.

---

## 3. Expected Pydantic Models

At minimum:
- `GscSiteEntry` — site URL + permission level
- `GscSearchAnalyticsRow` — date, query/page/country/device dimension + impressions, clicks, ctr, position
- `GscSearchAnalyticsResponse` — rows + aggregation totals
- `GscTokens` — access_token, refresh_token, expires_at
- `GscTokenStore` — protocol for persistent token storage (ABC or Protocol)

**Normalization rule:** All date fields are `date` objects. All numeric fields are `float` (CTR can be ratio or None). Position is `float`.

---

## 4. Required Tests

### Unit Tests (test_gsc_client.py)
- `test_list_sites_returns_normalized_site_entries` — mock the HTTP response, verify GscSiteEntry list
- `test_get_search_analytics_returns_normalized_rows` — mock response, verify row count, field types
- `test_handles_empty_response_gracefully` — empty rows list, no exception
- `test_handles_missing_config_raises_clean_error` — missing credentials raises `GscConfigError` (not bare `Exception`)
- `test_token_store_save_and_load` — verify token persistence round-trip

### Router Tests (test_gsc_router.py) — if router included
- `test_gsc_health_returns_200` — router health
- `test_list_sites_endpoint_returns_401_without_auth` — unauthenticated request
- `test_search_analytics_rejects_missing_params` — validation error on missing site_url/start_date/end_date

### Integration with Existing Tests
- All 22 existing tests in `tests/` must still pass after GSC slice is merged
- Run: `PYTHONPATH=. python -m pytest tests/ -q` — must be 22/22 green

---

## 5. Mocking Strategy

### GscClient must be mockable via dependency injection

The router (if any) must accept `GscClient` as a dependency:

```python
# Router pattern:
@router.get("/sites")
async def list_sites(client: GscClient = Depends(get_gsc_client)):
    ...
```

`get_gsc_client` reads from request state or app state, not a global singleton. This allows test overrides with `app.dependency_overrides[get_gsc_client] = lambda: MockGscClient()`.

**No live API calls in tests.** All tests mock httpx responses using `AsyncClient` with a mock transport or by patching `GscClient._request`.

---

## 6. Config / Env Expectations

### Required env vars (from .env.example)
```
GOOGLE_API_KEY=...              # NOT used for GSC OAuth2 — GSC uses client_id/secret
GOOGLE_SEARCH_CONSOLE_CLIENT_ID=...
GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET=...
GOOGLE_SEARCH_CONSOLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### Config pattern
`Services.api.config.Settings` should expose `google_search_console_client_id`, `google_search_console_client_secret`, `google_search_console_redirect_uri` as optional fields with defaults of `None`.

If credentials are absent, `GscClient.__init__` should raise `GscConfigError("GSC credentials not configured")` — not silently succeed with broken state.

---

## 7. Security Concerns

1. **No secrets in code or tests** — client_secret, tokens, API keys never appear in source files. Use `os.environ.get()` or Settings fields.

2. **Token storage** — tokens must not be logged or exposed in error messages. Refresh tokens must be stored securely (DB field, not plain text in memory).

3. **No live API calls in tests** — patch `httpx.AsyncClient.post` / `httpx.AsyncClient.get` to return fixture data. Real calls require valid OAuth tokens and hit GSC servers.

4. **Redirect URI validation** — the redirect_uri in requests must match the registered URI exactly.

5. **State parameter in OAuth** — use a random state string to prevent CSRF in authorization URL flow.

6. **Error message sanitization** — API error responses from GSC may contain sensitive data. Log raw responses at DEBUG level only; surface user-facing messages must not leak tokens or internal IDs.

---

## 8. No-Secret Rules

These patterns must NOT appear in any committed file:
- `client_secret = "..."` or `client_secret = '...'`
- `access_token = "..."` or `refresh_token = "..."`
- Real OAuth codes or tokens in test fixtures
- `os.environ.get("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "real_secret")`

Use `pytest.fixture` with `monkeypatch` for test setup, or environment variable files that are gitignored.

---

## 9. No-Live-API-Call Testing Rules

1. **All HTTP calls mocked** — patch `GscClient._request` or `httpx.AsyncClient` at the test module level
2. **Use `AsyncClient` with mock transport** in router tests — never `httpx.AsyncClient` that connects to real hosts
3. **Fixtures for GSC API responses** — store example JSON responses as Python dicts in `tests/fixtures/gsc_responses.py`
4. **No `pytest.mark.integration`** tests that hit live APIs — those go in a separate `tests/integration/` directory and are skipped in normal CI

---

## 10. Acceptance Checklist

Copy and check each item when reviewing the GSC branch:

```
FILE PRESENCE
[ ] packages/integrations/gsc_client.py exists
[ ] packages/integrations/gsc_models.py exists (or inline in gsc_client.py)
[ ] tests/test_gsc_client.py exists with ≥5 tests
[ ] (if router included) tests/test_gsc_router.py exists

IMPORT CLEANLINESS
[ ] PYTHONPATH=. python -c "from packages.integrations.gsc_client import GscClient" succeeds
[ ] No import errors from adding GSC files

TEST CLEANLINESS
[ ] PYTHONPATH=. python -m pytest tests/test_gsc_client.py -v — all pass
[ ] PYTHONPATH=. python -m pytest tests/ -q — 22 existing tests still green (not 21)

NO LIVE API CALLS
[ ] No httpx client making real HTTP requests in test files
[ ] All HTTP responses come from mocked fixtures
[ ] No GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET value in any test file

CONFIG HANDLING
[ ] Missing credentials raises GscConfigError (not bare Exception)
[ ] GscClient handles missing token gracefully (clears and re-auths)
[ ] list_sites normalizes site_url to strip trailing slash

DATA NORMALIZATION
[ ] get_search_analytics returns rows with date objects (not strings)
[ ] CTR field handles None (no clicks → None CTR, not divide-by-zero)
[ ] Position is float, not int

ERROR HANDLING
[ ] Expired token triggers refresh, retry once
[ ] HTTP 429 (rate limit) raises GscRateLimitError (custom exception)
[ ] HTTP 401/403 raises GscAuthError
[ ] Network timeout raises GscConnectionError

ROUTER (if included)
[ ] GET /api/v1/gsc/sites returns 200 or 401 (not 500)
[ ] GET /api/v1/gsc/analytics requires site_url, start_date, end_date params
[ ] All responses are JSON (application/json)

DOCS
[ ] AGENT_HANDOFF.md updated with GSC work
[ ] docs/INTEGRATIONS.md added or updated with GSC connector documentation
[ ] docs/TASK_BOARD.md updated with GSC slice as done

SCOPE DISCIPLINE
[ ] No changes to services/api/routers/ (unless explicitly scoped)
[ ] No changes to packages/seo_audit/ or packages/geo_audit/
[ ] No changes to packages/content_engine/ or packages/schema_engine/
[ ] No new database migrations unless explicitly required
[ ] No frontend changes
```

---

## 11. Merge-Readiness Checklist

Before recommending merge:

- [ ] All acceptance checklist items pass
- [ ] `git diff origin/feature/backend-phase2 --stat` shows only GSC-related files
- [ ] No `.env` file or secrets accidentally committed
- [ ] `PYTHONPATH=. python -m pytest tests/ -q` → 22/22 (or N+existing)
- [ ] Code review notes: no placeholder comments (TODO: implement...), no commented-out code
- [ ] GSC OAuth flow documented in docs/INTEGRATIONS.md

---

## 12. Follow-Up Task Recommendations

After reviewing `feature/gsc-integration-slice`:

1. **Wire GSC data into SEO audit flow** — top queries from GSC → keyword research pipeline → ContentBrief generation
2. **Add GA4 client** — GA4Client in `packages/integrations/ga4_client.py`, following GSC patterns
3. **Token storage implementation** — currently `GscTokenStore` is a Protocol/ABC. Implement SQLite-backed storage for local dev, PostgreSQL-backed for production
4. **Add PageSpeed client** — `packages/integrations/pagespeed_client.py` for Core Web Vitals data
5. **Update API_SPEC.md** — document GSC endpoints with request/response examples
6. **Production GSC credentials** — once branch is merged, user must add real OAuth2 credentials to `.env`

---

## Key Risks

### 1. OAuth2 token management complexity
GSC uses OAuth2 with refresh tokens. If the token store interface is too abstract (just a Protocol), there may be no working implementation for local dev. **Watch for:** `GscTokenStore` has no concrete implementation and `get_gsc_client` always fails.

### 2. Rate limit handling missing
GSC has tight rate limits. If the client doesn't handle 429s with backoff, the integration will be fragile in production. **Watch for:** no `GscRateLimitError` or exponential backoff in `gsc_client.py`.

### 3. Normalization gaps
GSC API returns `ctr` as a ratio (0–1) or as a percentage depending on dimension granularity. If normalization is wrong, downstream scoring will be off. **Watch for:** CTR values that are 10x or 100x what they should be.

### 4. Scope creep — router changes
The GSC slice may include FastAPI router additions to `services/api/routers/`. This is adjacent to existing routers (businesses, websites, crawls) and could conflict. **Watch for:** changes to `services/api/routers/` that aren't in scope.

### 5. Test pollution
Tests may mock at too high a level (patching `GscClient` entirely) rather than at the HTTP layer, making them pass even when the underlying HTTP logic has bugs. **Watch for:** `mock.patch("packages.integrations.gsc_client.GscClient")` at module level rather than `mock.patch.object(client, "_request")`.

---

## Base Branch State (reference)

```
Branch: feature/backend-phase2
Base commit: 0fb1772 (docs: add Phase 2 documentation foundation)
Previous: 16f6d25 — not on this branch. Expected base was 16f6d25 and 0fb1772; current HEAD is 0fb1772.
```

The branch is at `0fb1772` (7 commits ahead of the Step Flash audit base `2b62fee`).

---

*Document created by MiniMax Secondary Reviewer on `review/phase2b-gsc-review-plan`*