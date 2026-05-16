# MTVSEO-RUN-AUDIT-FLOW-CONTRACT-001 — Mr.R9 Handoff

## Task ID
MTVSEO-RUN-AUDIT-FLOW-CONTRACT-001-R9-BUILD

## Branch
`feature/run-audit-flow-contract-001`

## Base Branch
`origin/feature/backend-phase2`

## Starting Commit
`9fdb3a1` — Merge feature/audits-pagination-crawl-filter-001: audits pagination + crawl_run_id filter (MTV-36)

## Ending Commit
`ca4558b` — feat(frontend): wire Run New Audit button to POST /api/v1/crawls/

## Files Changed (3 files, +117/-10 lines)
```
apps/web/src/lib/api/client.ts        | 11 +++++
apps/web/src/lib/queries/useCrawls.ts | 28 +++++++++-
apps/web/src/app/audits/page.tsx      | 88 ++++++++++++++++++++++++++++++----
3 files changed, 117 insertions(+), 10 deletions(-)
```

---

## Implementation Summary

### 1. apiPost (apps/web/src/lib/api/client.ts)

Added `apiPost<T>(path: string, body: unknown): Promise<T>` following the exact same pattern as `apiGet`:
- Uses `normalizeUrl(path)` for consistent URL construction
- `method: "POST"`, `Content-Type: application/json`, `credentials: "include"`
- JSON-serializes body
- `handleResponse` for error extraction (same as GET, non-2xx throws `ApiError`)
- Does not break `apiGet`

### 2. useCreateCrawl (apps/web/src/lib/queries/useCrawls.ts)

Added `useCreateCrawl()` mutation:
- Uses `@tanstack/react-query` `useMutation`
- `mutationKey: ["crawls", "create"]`
- Payload type: `CreateCrawlPayload { website_id: string; crawl_depth?: number; max_pages?: number; respect_robots?: boolean }`
- Response type: `CrawlRun` (matches existing `CrawlRun` type in types/crawls.ts)
- Calls `apiPost<CrawlRun>(API_ROUTES.CRAWLS, payload)` → `POST /api/v1/crawls/`
- `onSuccess`: invalidates `["crawls", "list"]` query key to refetch crawl list
- Error type: `ApiError` from `@/lib/api/client`

### 3. Audits Page Button (apps/web/src/app/audits/page.tsx)

**Imports added:**
- `useWebsites` from `@/lib/queries/useWebsites`
- `useCreateCrawl` from `@/lib/queries/useCrawls`
- `PlayCircle` icon from lucide-react
- Renamed `Loader2` to `Spinner` to avoid collision with the loading spinner in the issues table

**Website selector:**
- Uses `useWebsites()` to fetch available websites
- Shows loading text while websites load
- Shows "No websites available. Add a website first." if zero websites exist
- Renders `<select>` dropdown with website URL options (preselected to empty)

**Button states:**
- `disabled` when: no website selected OR mutation pending OR no websites exist
- `isCreating` (mutation pending) → shows spinner + "Queuing..." text
- Idle → shows `PlayCircle` icon + "Run New Audit"

**handleRunAudit behavior:**
- If no `website_id` selected → sets error feedback "Please select a website first."
- Calls `createCrawl.mutate({ website_id: selectedWebsiteId })`
- `onSuccess`: sets success feedback "Audit queued for selected website. Results will appear after processing."
- `onError` (err): sets error feedback "Audit request failed: {err.message}"

**Feedback banner:**
- Green/emerald banner for success state
- Red banner for error state
- Dismissed automatically on next button click

---

## Honesty Verification

| Requirement | Status |
|---|---|
| No fake completed audit | ✅ No such language anywhere |
| No fake SEO issues | ✅ Not introduced |
| No fake crawl progress | ✅ Not introduced |
| No fake score | ✅ Not introduced |
| No fake report generated | ✅ Not introduced |
| No silent website selection | ✅ Website selector always visible, selected website always shown |
| Success message is honest | ✅ "Audit queued... Results will appear after processing." |
| Error message is honest | ✅ "Audit request failed: {API error}" |
| reports/page.tsx not modified | ✅ |
| Backend files not modified | ✅ |

---

## Commands Run

```bash
cd /home/mtv/Projects/seo-agent-os
git fetch origin
git checkout origin/feature/backend-phase2 -b feature/run-audit-flow-contract-001

# Implemented apiPost, useCreateCrawl, Audits page wiring

cd apps/web && npm install
cd apps/web && npm run build
# Build passed: all routes compiled, TypeScript checks passed

npm run lint
# ESLint not configured — skipped
```

### Build Output
```
Route (app)                              Size     First Load JS
┌ ○ /                                    5.09 kB         112 kB
├ ○ /_not-found                          873 B            88 kB
├ ○ /audits                              4.61 kB         111 kB
├ ○ /businesses                          2.3 kB         98.8 kB
└ ○ /reports                             3.11 kB         110 kB
```

---

## Known Risks

1. **No-website state UX**: The spec says "disable the button and show an honest message." Button is disabled + a message is shown. This is acceptable per spec.

2. **No crawl depth / max_pages controls**: Spec payload fields `crawl_depth`, `max_pages`, `respect_robots` are optional. Button sends only `website_id`. Optional fields not exposed in UI — this matches "minimal viable wiring" and honest behavior (no fake config).

3. **No cancel/retry UX for failed requests**: After a failed request, the user must click the button again. No persistent error state. This is acceptable per the acceptance criteria.

---

## Next Step for Mr.R7

Mr.R7 should independently verify:
1. `apiPost` works correctly with the backend endpoint `POST /api/v1/crawls/`
2. The website selector properly fetches and displays websites
3. The "Run New Audit" button shows loading/queued state correctly
4. No fake data is rendered after a successful crawl request
5. The button is disabled when no website is selected
6. `reports/page.tsx` was not modified
7. Backend files were not modified
8. `npm run build` passes

Mr.R7 should also confirm the scope matches the spec exactly and produce a verification handoff doc.