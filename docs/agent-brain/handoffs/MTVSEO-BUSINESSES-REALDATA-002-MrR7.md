# MTVSEO-BUSINESSES-REALDATA-002 — Mr.R7 QA Handoff

## Status

APPROVED_FOR_GATEKEEPER

## Branch Inspected

`feature/businesses-page-realdata-002`

## QA Verdict

APPROVED_FOR_GATEKEEPER — Mock data removed cleanly, real API wired correctly, all honest states present, build passes, compileall passes.

## Files Reviewed

| File | Review Notes |
| ---- | ------------ |
| `apps/web/src/app/businesses/page.tsx` | Complete rewrite — hardcoded `const businesses` array removed, `useBusinesses()` hook wired, honest loading/error/empty states added, real API fields rendered, SEO Score and Last Crawl honestly show `—` |
| `apps/web/src/lib/queries/useBusinesses.ts` | Clean hook — calls `GET /api/v1/businesses/`, returns `BusinessListResponse`, no fake fallback |
| `apps/web/src/lib/api/types/businesses.ts` | Types aligned with page rendering: `id`, `name`, `website_url`, `business_type`, `location`, `is_cannabis`, `is_ymyl` |
| `apps/web/src/lib/api/routes.ts` | `BUSINESSES: "/api/v1/businesses/"` — correct API route |
| `docs/agent-brain/handoffs/MTVSEO-BUSINESSES-REALDATA-002-MrR9.md` | Builder handoff — complete, accurate, lists all changes and known limitations |

## Mock/Fake Data Audit

| Item | Active Source Match? | Verdict | Notes |
| ---- | -------------------- | ------- | ----- |
| MTV Tech Solutions | NO | PASS | Removed from page |
| Green Culture | NO | PASS | Removed from page |
| Country Roads Car Services | NO | PASS | Removed from page |
| `const businesses = [...]` | NO | PASS | Hardcoded array removed |
| `businesses = [` | NO | PASS | No match in active source |
| `2h ago` / `1d ago` / `2d ago` | NO | PASS | Removed from page |
| Hardcoded SEO scores | NO | PASS | Removed from page |
| Fake placeholder in `useBusinesses` | NO | PASS | Hook returns no fake fallback |
| `placeholder` in search input | YES (but OK) | NOT A BLOCKER | Standard HTML placeholder attribute, not fake data |
| `MoreHorizontal` icon removed | YES (but OK) | NOT A BLOCKER | Cleanup of unused import |

Grep on `apps/web/src/app/businesses/` and `apps/web/src/lib/` returned only `placeholder="Search businesses..."` — a standard HTML input attribute, not fake business data. No user-facing hardcoded business rows remain.

## Businesses Page Behavior

| State | Behavior | Verdict |
| ----- | -------- | ------- |
| Loading | Centered "Loading businesses..." text in slate-500 | PASS — honest |
| Error | Centered "Failed to load businesses." in red-400 | PASS — honest |
| Empty | Centered Building2 icon + "No businesses yet." + "Add a business to get started." | PASS — honest |
| Data loaded | Maps `data.items` to business rows with name, website_url, business_type/location, Cannabis/YMYL badges | PASS — real data |
| Add Business button | Disabled with tooltip "Create flow coming soon" — bg-blue-600/50, text-white/50, cursor-not-allowed | PASS — honest, no create page exists |
| Search input | Non-functional client-side search bar (placeholder only, no actual filtering) | PASS — matches original design, no regression |

## API Wiring Review

| Item | Verdict | Notes |
| ----- | ------- | ----- |
| `useBusinesses` hook | PASS | Calls `apiGet<BusinessListResponse>(API_ROUTES.BUSINESSES)` = `GET /api/v1/businesses/` |
| API route | PASS | `BUSINESSES: "/api/v1/businesses/"` — correct real endpoint |
| Type alignment | PASS | `Business.id`, `Business.name`, `Business.website_url`, `Business.business_type`, `Business.is_cannabis`, `Business.is_ymyl` all used in page rendering |
| No fake fallback data | PASS | Hook returns React Query state only; no hardcoded fallback arrays |

## Verification Results

| Check | Result | Notes |
| ----- | ------ | ----- |
| python scripts/verify_local.py | FAIL (ENV) | MTVSEO Python venv not activated — missing fastapi, pydantic, sqlalchemy, etc. Not a code failure. |
| pytest tests/ -q | FAIL (ENV) | Same environment gap (venv not activated). Not a code failure. |
| python -m compileall services packages tests scripts | PASS | All .py files compile cleanly, exit 0 |
| cd apps/web && npm install && npm run build | PASS | Next.js 14 build clean, /businesses route 1.97 kB |
| mock/fake grep (MTV Tech / Green Culture / businesses = / 2h ago) | PASS | No hardcoded mock data in active source |
| git diff --stat | PASS | Only 2 files changed: page.tsx (-66, +137 lines) and handoff doc |

## Regression Risk

LOW

- Only `apps/web/src/app/businesses/page.tsx` changed — no backend, no auth, no other pages
- Search input was already non-functional before this change (documented as known limitation)
- All compileall and build checks pass
- The `/audits`, `/reports`, `/` pages are completely unaffected

## Required Fixes

None.

## Non-Blocking Observations

1. **Search input is non-functional** — the search bar filters nothing. This was already the case before this change. A client-side filter on `data.items` or a backend search param would fix it, but it's not a regression.

2. **Add Business button is disabled** — no create page exists yet. Honest and correct.

3. **SEO Score and Last Crawl show `—`** — no backend endpoint provides these on the Business model yet. Honest and correct.

4. **No pagination controls** — `useBusinesses()` fetches with backend `limit=20`. No load-more UI added. Not a regression.

5. **npm audit has 5 vulnerabilities** (1 moderate, 3 high, 1 critical) — pre-existing, not introduced by this branch.

## Recommendation to Mr.M1

**APPROVE FOR GATEKEEPER REVIEW**

Rationale:
- Mock data (MTV Tech Solutions, Green Culture, Country Roads Car Services, hardcoded SEO scores, hardcoded crawl times) fully removed from active user-facing page code
- `useBusinesses()` hook correctly wired to `GET /api/v1/businesses/`
- All three honest states (loading/error/empty) correctly implemented
- SEO Score, Last Crawl, and Add Business button honestly show `—` or disabled rather than fake values
- compileall passes, npm build passes
- No regressions to other pages
- Builder handoff doc is complete and accurate