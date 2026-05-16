# MTVSEO-AUDITS-PAGE-PAGINATION-AND-CRAWL-FILTER-001 — Mr.R9 Handoff

## Branch Info
- **Branch**: `feature/audits-pagination-crawl-filter-001`
- **Base branch**: `feature/backend-phase2`
- **Starting commit**: `7b99ca8` (Merge feature/audits-page-realdata-001 into backend-phase2)
- **Ending commit**: `06588eb` (feature(frontend): audits page pagination and crawl_run_id filter)
- **Files changed**: `apps/web/src/app/audits/page.tsx`, `apps/web/src/lib/queries/useSeoIssues.ts`

---

## Changes to useSeoIssues

**File**: `apps/web/src/lib/queries/useSeoIssues.ts`

- New named export interface `UseSeoIssuesParams`:
  ```ts
  export interface UseSeoIssuesParams {
    crawlRunId?: string;
    skip?: number;
    limit?: number;
    pageId?: string;
  }
  ```
- `useSeoIssues()` now takes an optional params object `params: UseSeoIssuesParams = {}`
- Default `limit` changed from hardcoded `4` to `20` (`DEFAULT_LIMIT = 20`)
- Query key is now `["seo-issues", "list", params]` — React Query correctly caches per unique param combo
- `apiGet` URL is built via `buildUrl(params)` which appends `crawl_run_id`, `page_id`, `skip`, `limit` as query params

---

## Changes to Audits Page

**File**: `apps/web/src/app/audits/page.tsx`

### Architecture
- Page split into three components: `AuditsPage` (Suspense wrapper), `AuditsContent` (main), `AuditsLoading` (skeleton)
- `AuditsContent` is wrapped in `<Suspense fallback={<AuditsLoading />}>` — required by Next.js 14 for client-side `useSearchParams`
- `AuditsLoading` shows a simplified skeleton matching the page layout

### Pagination
- `PAGE_SIZE = 20` (matches `useSeoIssues` default)
- Local `skip` state managed via `useState(0)`
- **Load more button**: inline in the table header, advances `skip` by `PAGE_SIZE`
- **Pagination footer**: appears when `total > PAGE_SIZE`, shows "Showing X–Y of Z" with **First / Previous / Next** buttons
- `hasMore = skip + items.length < total` — uses real API `total`
- Changing severity resets `skip` to 0 so counts are consistent

### crawl_run_id Support
- Read from URL via `useSearchParams().get("crawl_run_id")` inside `AuditsContent`
- When `crawl_run_id` is present, a small "filtered by crawl" label appears in the header subtitle
- Passed to `useSeoIssues({ crawlRunId, skip, limit: PAGE_SIZE })`
- When absent, all issues are shown (no fake context)

### States Preserved
| State | Behavior |
|-------|----------|
| Loading | Skeleton rows in header, spinner in table body |
| Error | AlertTriangle icon + error message, no crash |
| Empty (no issues at all) | Centered empty state with "Run a crawl" note |
| Filtered empty (severity) | "No {severity} severity issues." message |
| Populated | Full issue list rendered |

### Run New Audit Button
- **Not wired**. Left as a non-functional button in the header, unchanged from prior state.
- No fake crawl creation behavior added.

---

## How crawl_run_id is Accepted

`/audits?crawl_run_id=<uuid>` — passed as a URL query parameter. No crawl selector UI was added (scope control: URL param first approach per the task).

---

## How Pagination / Load-More Works

1. Page initializes with `skip=0`
2. `useSeoIssues({ skip, limit: PAGE_SIZE })` fetches items 0–19
3. API returns `{ items, total }` — `hasMore = skip + items.length < total`
4. **Load more** button increments `skip` by `PAGE_SIZE` → React Query refetches with new `skip`
5. **First** resets `skip` to 0
6. **Previous** decrements `skip` by `PAGE_SIZE` (floor at 0)
7. **Next** is disabled when `!hasMore`
8. Footer shows "Showing X–Y of Z" using real API `total`

---

## Empty / Error / Loading States

- **Loading**: `isLoading` → skeleton header cards + `<Loader2>` spinner in table
- **Error**: `isError` → `<AlertTriangle>` with message
- **Empty (total=0, all)**: centered `<CheckCircle2>` + "No SEO issues found" + "Run a crawl" note
- **Filtered empty (severity)**: centered `<CheckCircle2>` + "No {severity} severity issues."
- **Populated**: renders issue rows, shows severity breakdown cards

---

## Strict Non-Goals Confirmed

- ❌ No fake/mock/static SEO issue data
- ❌ No fake crawl/audit behavior
- ❌ Run New Audit button not wired
- ❌ No backend files modified
- ❌ No reports/businesses/dashboard changes
- ❌ No build artifacts committed

---

## Commands Run

```bash
# git status (clean before work)
git status
# → On branch feature/backend-phase2, nothing to commit, working tree clean

# Create feature branch
git checkout -b feature/audits-pagination-crawl-filter-001

# Edit useSeoIssues.ts and audits/page.tsx

# npm install
cd apps/web && npm install
# → (no changes, deps already satisfied)

# Build
cd apps/web && npm run build
# → ✓ Compiled successfully, all 7 static pages generated

# Diff vs base
git diff --stat origin/feature/backend-phase2
# → apps/web/src/app/audits/page.tsx | 112 ++++++++++---
# → apps/web/src/lib/queries/useSeoIssues.ts |  29 ++++++--

# Commit
git add -f apps/web/src/lib/queries/useSeoIssues.ts apps/web/src/app/audits/page.tsx
git commit -m "feature(frontend): audits page pagination and crawl_run_id filter..."
# → [feature/audits-pagination-crawl-filter-001 06588eb] 2 files changed, 127 insertions(+), 14 deletions(-)
```

---

## Known Risks

1. **crawl_run_id URL param only** — if a user expects a crawl selector dropdown, they won't find one. This is scope-controlled; URL param is the agreed-upon approach for this slice.
2. **Pagination state is client-side only** — if the page is refreshed, skip resets to 0. Acceptable for this slice; URL-synced pagination would be a separate enhancement.
3. **Severity filter resets skip** — intentional so counts stay consistent within the filtered set.

---

## Next Step for Mr.R7

Mr.R7 should independently verify:
1. `npm run build` in `apps/web` passes cleanly on this branch
2. `useSeoIssues` accepts `crawlRunId`, `skip`, `limit` params and builds correct URL
3. The audits page renders more than 4 issues when API returns > 4
4. `total` from API is used for pagination controls (not a hardcoded value)
5. `?crawl_run_id=` URL param is read and passed to `useSeoIssues`
6. Run New Audit button is NOT wired to any new behavior
7. No fake data or backend files were introduced

Branch: `feature/audits-pagination-crawl-filter-001`
Base: `origin/feature/backend-phase2` → compare `06588eb` vs `7b99ca8`
