# MTVSEO-DASHBOARD-REALDATA-001 — Mr.R9 Builder Handoff

## Status

COMPLETE — READY FOR QA / GATEKEEPER RE-REVIEW

## Branch

- **Feature branch:** `feature/dashboard-realdata-seo-issues-api`
- **Base branch:** `origin/feature/backend-phase2` (at commit `c263c07`)
- **Commit:** `5978eea` ("fix(frontend): remove hardcoded mock data from dashboard page.tsx")

## Objective

Remove all hardcoded/fake user-facing mock data from the dashboard (`apps/web/src/app/page.tsx`) so the four real API-backed panels show honest empty states instead of fabricated data. No production code changed other than removing mock UI sections.

## Summary of Changes

Commit `5978eea` removed the following hardcoded mock UI from the dashboard:

1. **`metrics` KPI card array** — 4 cards (Technical SEO, GEO/AI Visibility, Content Quality, Crawl Health) with hardcoded values, grades, and trends
2. **`keywordOpportunities` table** — 3 hardcoded SEO keyword rows (emergency hvac repair, commercial hvac maintenance, geothermal heating)
3. **Unused imports** — `MetricCard` component and icons (`ExternalLink`, `TrendingUp`, `LineChart`, `Zap`)

After this change, all four dashboard panels now depend entirely on real API hooks (`useBusinesses`, `useWebsites`, `useCrawls`, `useSeoIssues`) and show honest empty-state UI when no data exists.

## Files Changed

| File | Change |
| ---- | ------ |
| `apps/web/src/app/page.tsx` | −88 lines, +2 lines: removed hardcoded mock data arrays, removed `MetricCard` import, removed unused icon imports |

## Fake/User-Facing Mock Data Removed

| Removed Item | Type | Detail |
| --- | --- | --- |
| `metrics` array | KPI card data | Technical SEO (72/C), GEO/AI Visibility (58/D), Content Quality (81/B), Crawl Health (94/A) |
| `keywordOpportunities` array | Keyword table | "emergency hvac repair", "commercial hvac maintenance", "geothermal heating" with fake volume/difficulty/position/change |
| `MetricCard` import | Component | `<MetricCard>` used only by removed `metrics` array |
| `ExternalLink`, `TrendingUp`, `LineChart`, `Zap` | Icon imports | Only used by removed mock sections |

## Dashboard API Wiring Confirmation

| Panel | Hook | API Route | Verdict |
| --- | --- | --- | --- |
| Businesses | `useBusinesses()` | `/api/v1/businesses/` | ✓ Wired |
| Websites | `useWebsites()` | `/api/v1/websites/` | ✓ Wired |
| Crawl Runs | `useCrawls()` | `/api/v1/crawls/` | ✓ Wired |
| SEO Issues | `useSeoIssues()` | `/api/v1/seo-issues/` | ✓ Wired |

All four panels use React Query `useQuery` hooks with `apiGet` client pointing to FastAPI backend routes. Panels render honest empty-state when API returns no data.

## Verification Results

| Check | Result | Notes |
| --- | --- | --- |
| `pytest tests/ -q` | ✓ PASS | 40 passed in 2.36s |
| `python -m compileall services packages tests scripts` | ✓ PASS | All bytecode compilation clean |
| `python scripts/verify_local.py` | ✓ ALL CHECKS PASSED | redis, alembic, pytest, ruff, all package imports, FastAPI app, /health, DB config |
| `cd apps/web && npm install && npm run build` | ✓ PASS | ✓ Compiled successfully, all 7 static pages generated |

## Known Limitations / Follow-Ups

| Item | Status | Notes |
| --- | --- | --- |
| KPI cards removed | Pending real metrics API | Four MetricCard slots empty until `/api/v1/metrics` or equivalent exists |
| Keyword Opportunities removed | Pending real keyword API | Table removed entirely; no keyword endpoint wired yet |
| Hardcoded "MTV Tech Solutions" | Follow-up | Line 78 in `page.tsx`: `<span className="text-blue-400 font-medium">MTV Tech Solutions</span>` — needs dynamic business name |
| Static "Last sync: 5 min ago" | Follow-up | Line 88 in `page.tsx`: hardcoded relative time — needs real last-sync timestamp from API |
| `MetricCard` component orphaned | Follow-up | `apps/web/src/components/metric-card.tsx` exists but is no longer imported anywhere |

## Handoff to Mr.R7

Mr.R7: Please pull branch `feature/dashboard-realdata-seo-issues-api` and perform QA review. Key things to verify:

1. All four panels (Businesses, Websites, Crawl Runs, SEO Issues) render empty-state UI when no backend data exists
2. The removed mock sections (KPI cards, Keyword Opportunities) no longer appear in the dashboard
3. The three follow-up items above (MTV Tech Solutions hardcode, static "Last sync", orphaned MetricCard) are tracked as separate follow-up issues

## Handoff to Mr.M1

Mr.M1: The missing builder handoff artifact has been created at:

`docs/agent-brain/handoffs/MTVSEO-DASHBOARD-REALDATA-001-MrR9.md`

This resolves the blocker cited in the gatekeeper review. The branch `feature/dashboard-realdata-seo-issues-api` at commit `5978eea` is ready for re-review.
