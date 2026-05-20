# Handoff: MTVSEO-OPERATIONS-DASHBOARD-REALDATA-001-MrR9

## Branch
`feature/operations-dashboard-realdata-001` (2 commits ahead of `origin/feature/backend-phase2`)

## Commits

### Commit 1 — f8c2ef0
```
dashboard: wire real totals, remove dead links, fix Score col, fix nav links

- Remove Score column from Recent Crawls table (CrawlRun has no score field)
- Update Quick Action 'New Crawl' href: /businesses -> /websites
- Update 'View all' link for Recent Crawls: /businesses -> /audits
- Remove dead Link on /businesses rows (no /businesses/[id] route exists);
  change to plain div with no hover/link styling
- Use site.name ?? site.url (Website.name is nullable but available)
- No MOCK_ constants, no fake data, no new dependencies
```

### Commit 2 — b2bf420
```
dashboard: add summary stat cards wiring total fields

Add 4 summary stat cards (Businesses, Websites, Crawl Runs, SEO Issues)
using response.total with items.length fallback for defensive rendering.
Cards show '—' during loading state.
```

## Files Changed
- `apps/web/src/app/page.tsx` — Summary stat cards, Score col removal, nav link fixes
- `apps/web/src/app/businesses/page.tsx` — Dead link removal (a -> div)

## Hooks Used
- `useBusinesses()` → `BusinessListResponse.total`, `BusinessListResponse.items.length`
- `useWebsites()` → `WebsiteListResponse.total`, `WebsiteListResponse.items.length`
- `useCrawls()` → `CrawlListResponse.total`, `CrawlListResponse.items.length`
- `useSeoIssues()` → `SeoIssueListResponse.total`, `SeoIssueListResponse.items.length`

## Routes Touched
- `/` (dashboard page) — summary stats, crawl table, website panel
- `/businesses` — dead link removal

## Build Result
```
cd apps/web && npm run build
✓ Compiled successfully
✓ Generating static pages (8/8)
All routes: /, /_not-found, /audits, /businesses, /crawls/[id], /reports, /websites, /websites/[id]
```

## Fake-Data Check
```bash
$ rg -i 'mock\|fake\|MOCK_' apps/web/src
(no output — clean)
```

## Known Limitations
- Summary stat cards use `total` from API responses, but `useWebsites` and `useCrawls` hardcode `limit=4` — `total` reflects total count across all pages, while `items.length` reflects the single fetched page. When total > items shown, this is intentional (true total across all records).
- Business rows on `/businesses` are no longer clickable (no detail route exists).
- Business rows on dashboard Business Projects panel are also not clickable (same reason).
- Website identifier in dashboard panel still shows `business_id.slice(0,8)` as fallback since `site.name` may be null and no website name lookup hook exists on the dashboard context.