# Handoff: MTVSEO-CRAWL-DETAIL-ISSUES-REALDATA-001

## Task ID
MTVSEO-CRAWL-DETAIL-ISSUES-REALDATA-001

## Branch
`feature/crawl-detail-issues-realdata-001`

## Builder
@Mr.R9

## Verifier
@Mr.R7

---

## Starting Commit
`332b9d3a9c8c9a9888395e13a1bc72a2285a5a3f` (origin/feature/backend-phase2)

## Ending Commit
`4bda5b0` (local HEAD on feature/crawl-detail-issues-realdata-001)

## Files Changed
- `apps/web/src/app/crawls/[id]/page.tsx`

## Summary of Work
Added a "SEO Issues" section to the `/crawls/[id]` page that shows real SEO issues linked to the crawl run via `crawl_run_id`.

- Uses `useSeoIssues({ crawlRunId: crawlId, limit: 50 })` — backend API supports `crawl_run_id` filter natively (router `seo_issues.py` line 19)
- Shows severity badge, title, description, issue_type, and relative time
- Loading, error, and honest empty states (no issues = "No SEO issues found for this crawl run.")
- Mirrors the same pattern already used on the website detail page's `SeoIssuesSection`
- No fake data, no hardcoded arrays, no backend changes

## Real API / Hooks Used
- `useSeoIssues` from `@/lib/queries/useSeoIssues` (supports `crawlRunId` filter)
- `useCrawl` (already used in the page)
- `SEVERITY_LABELS`, `SEVERITY_VARIANTS` from `@/lib/api/types/seo_issues`

## Backend Touched
NO

## Fake-Data Grep Result
NO_FAKE_DATA_FOUND (only `placeholder` in search input `placeholder` attrs, which are UI text not fake data)

## Build Artifact Status
NO_BUILD_ARTIFACT

## Build Result
PASS — `npm run build` succeeds, `/crawls/[id]` is 6.23 kB + 118 kB first load JS

## Known Limitations
- The SEO issues section filters by `crawl_run_id` only (as required by the API). If a crawl has no issues, the honest empty state is shown.
- `websiteId` prop is accepted by `SeoIssuesSection` but not used (kept for future flexibility if we ever need to fall back to website-level issues).

## Commit Hash
`4bda5b0`

## Push Status
Pushed to `origin/feature/crawl-detail-issues-realdata-001`

## Next Recommended Action
@Mr.R7 — verify branch, run fake-data grep, run build, report PASS or CHANGES_REQUESTED.