# Handoff: MTVSEO-WEBSITE-ISSUES-REALDATA-001

**Agent:** Mr.R9
**Date:** 2026-05-17
**Task ID:** MTVSEO-WEBSITE-ISSUES-REALDATA-001
**Branch:** feature/website-issues-realdata-001
**Commit:** b5d972c

---

## Summary

Added a real SEO issues section to the website detail page (`apps/web/src/app/websites/[id]/page.tsx`) that shows SEO issues from real API data, filtered client-side by the website's crawl run IDs.

---

## Start / End Commits

- **Starting commit:** `f30bb33` (current origin/feature/backend-phase2 at time of branch)
- **Ending commit:** `e1f90ff` (feat: show real SEO issues on website detail)

---

## Files Changed

- `apps/web/src/app/websites/[id]/page.tsx` (+140 lines)

---

## Implementation Details

### Hook Reused
- `useSeoIssues` from `@/lib/queries/useSeoIssues`
- `SEVERITY_LABELS`, `SEVERITY_VARIANTS` from `@/lib/api/types/seo_issues`

### SEO Issue API Shape Observed
```typescript
interface SeoIssue {
  id: string;
  page_id: string | null;
  crawl_run_id: string;
  issue_type: string;
  severity: IssueSeverity; // "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO"
  title: string;
  description: string | null;
  recommendation: string | null;
  affected_element: string | null;
  created_at: string;
  updated_at: string;
}
```

### Filtering Approach
- **website_id filtering:** NOT supported by API. `SeoIssue` records have no `website_id` field.
- **crawl_id relationship:** SUPPORTED. `SeoIssue.crawl_run_id` links to real crawl runs.
- **Client-side filtering:** Issues are filtered by matching `crawl_run_id` against the website's real crawl run IDs fetched via `useWebsiteCrawls(websiteId)`.

### Workflow
1. `SeoIssuesSection` first fetches crawl runs for the website via `useWebsiteCrawls`
2. If no crawls exist → empty state
3. If crawls exist → fetches all SEO issues via `useSeoIssues({ limit: 50 })`
4. Client-side filters `data.items` to those whose `crawl_run_id` is in the website's crawl IDs

---

## UI States Implemented

- **Crawls loading:** Shows "Loading crawl history first..." spinner
- **No crawl runs:** Shows empty state with prompt to run a crawl
- **Issues loading:** Shows "Loading SEO issues..." spinner
- **Issues error:** Shows error state with "Check that the backend is running"
- **Issues empty:** Shows "No SEO issues found for this website" with honest message
- **Issues success:** Shows issue list with severity badges, title, description, type, and timestamp

---

## Fake-Data Grep Result

```
NO_FAKE_ISSUE_DATA_FOUND
```

Command: `grep -RInE "MOCK|mock|fake|sample|demo|mtvhvaccom|green-cultureco|countryroadsautocom|seoScore|geoScore|issues\s*=\s*|const\s+issues\s*=\s*|seoIssues\s*=\s*|const\s+seoIssues\s*=\s*|auditFindings\s*=\s*|const\s+auditFindings\s*=\s*" apps/web/src/app apps/web/src/lib`

---

## Build Result

```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Generating static pages (8/8)

Route (app)                              Size     First Load JS
└ ƒ /websites/[id]                       4.39 kB         116 kB
```

Build artifact (`tsconfig.tsbuildinfo`): **NOT PRESENT**

---

## Known Limitations

1. **No API-level website_id filter:** The backend SEO issues API only supports `crawl_run_id`, `page_id`, `skip`, and `limit` params. We cannot query issues by website_id directly. Client-side filtering via crawl run IDs is the safe workaround.
2. **Single global query:** `useSeoIssues({ limit: 50 })` fetches up to 50 most recent issues across all crawl runs. If a website has more than 50 issues across all its crawls, some may not appear. The API does not support per-crawl-run pagination from the frontend.
3. **No issue count per crawl run:** The UI shows total issue count from the global response, not per-crawl breakdown.

---

## Push Status

Branch pushed to `origin/feature/website-issues-realdata-001`.
Commit: `b5d972c`.