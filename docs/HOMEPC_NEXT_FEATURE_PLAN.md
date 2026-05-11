# Home PC Next Feature Plan

## Current State Summary

**Base branch:** `feature/backend-phase2` (commit `0fb1772`)
**Candidate branch:** `feature/ryzen9-api-wiring-businesses-next` (commit `34f0e66`)

The candidate branch completes the second frontend API wiring slice: wiring `GET /api/v1/businesses/` into the dashboard's "Business Projects" panel. It adds:

- `apps/web/src/lib/api/types/businesses.ts` — TypeScript `Business` + `BusinessListResponse` types
- `apps/web/src/lib/queries/useBusinesses.ts` — React Query hook
- `apps/web/src/app/page.tsx` — dashboard updated with business list panel
- `apps/web/src/lib/api/client.ts` — API client (`apiGet` wrapper) already in place
- `apps/web/src/lib/api/routes.ts` — `BUSINESSES` route constant pre-existing
- `apps/web/src/lib/api/types/crawls.ts` — `CRAWL_STATUS_LABELS` constant already in place

Also wired (prior slice): `useCrawls` → `GET /api/v1/crawls/` in the Recent Crawls table.

**Frontend stack now has:** API client, route constants, type files for businesses + crawls, React Query hooks for businesses + crawls, full dashboard wiring.

**Frontend still missing:** API types/hooks for websites, websites page, website detail page, any mutation hooks (create/update/delete).

---

## Recommended Next Slice

**Website Detail Page + Websites API Wiring**

Wire `GET /api/v1/websites/` into the `apps/web/src/app/businesses/page.tsx` (the businesses page currently shows hardcoded mock data). Then add a website detail page at `apps/web/src/app/websites/[id]/page.tsx` that shows:

- Website name, URL, associated business
- List of crawl runs (wired to `GET /api/v1/crawls/?website_id=<id>`)
- Crawl trigger button (opens the crawl creation flow)
- Crawl status display

This is the most natural next slice because:

1. Users navigate businesses → website detail → trigger crawl
2. All wiring patterns are already established (businesses wiring is the template)
3. The crawl trigger requires a website_id — you can't trigger a crawl without a website
4. No new backend endpoints needed (websites router + crawls router already exist)

---

## Why This Slice Comes Next

```
Dashboard (businesses list ✓ + crawls list ✓)
    ↓ (user clicks a business)
/businesses page (currently mock data — needs websites list wired)
    ↓ (user clicks a website)
/websites/[id] page (does not exist — needs new page)
    ↓ (user clicks "New Crawl")
Crawl creation modal or page (does not exist)
```

You cannot build the crawl trigger UI without a website context. The website detail page is a strict dependency for the crawl trigger slice. Wiring websites to the businesses page first means the user can see which websites belong to which business before drilling into the website detail.

Alternative slices and why they come later:
- **Crawl trigger from dashboard**: requires a selected website; dashboard has no website context
- **Business detail page**: nice-to-have but not a hard dependency for crawl flow
- **GSC integration**: Phase 3+ work, requires auth/OAuth setup
- **API client standardization**: can be done as a refactor alongside any slice
- **Authentication/user ownership**: backend concern, blocks nothing on frontend

---

## Files Likely Involved

**New files:**
- `apps/web/src/lib/api/types/websites.ts` — TypeScript `Website`, `WebsiteListResponse` types
- `apps/web/src/lib/queries/useWebsites.ts` — React Query hook `GET /api/v1/websites/`
- `apps/web/src/lib/queries/useWebsite.ts` — React Query hook `GET /api/v1/websites/{id}`
- `apps/web/src/app/websites/[id]/page.tsx` — new website detail page

**Modified files:**
- `apps/web/src/app/businesses/page.tsx` — replace mock data with `useWebsites` (keyed by business or global list)
- `apps/web/src/app/page.tsx` — optionally wire website count to dashboard KPI cards (stretch)
- `apps/web/src/lib/api/routes.ts` — confirm `WEBSITES` and `WEBSITE_BY_ID` route constants exist

**No backend files changed** (routers and schemas already exist).

---

## Backend Requirements

**Existing endpoints to wire:**
- `GET /api/v1/websites/` — returns `WebsiteList` (`{ items: Website[], total: number }`)
- `GET /api/v1/websites/{website_id}` — returns `WebsiteRead`
- `GET /api/v1/crawls/?website_id={id}` — filter crawls by website (verify this query param exists; if not, filter client-side)

**Backend models already in place:**
- `services/api/models/website.py` — Website model
- `services/api/schemas/website.py` — WebsiteCreate, WebsiteRead, WebsiteList schemas
- `services/api/routers/websites.py` — CRUD router already implemented
- `services/api/routers/crawls.py` — crawls router with filter support

**If `website_id` filter does not exist on `GET /api/v1/crawls/`, the frontend must filter client-side or the backend must be updated (minor).**

---

## Frontend Requirements

**Pages:**
- `apps/web/src/app/businesses/page.tsx` — wire `useWebsites` to replace mock business list (show website count per business)
- `apps/web/src/app/websites/[id]/page.tsx` — new page: website header, crawl run history table, "New Crawl" button

**Hooks:**
- `useWebsites(businessId?)` — list websites, optionally filtered by business
- `useWebsite(id)` — fetch single website by ID

**Components (reuse existing):**
- `StatusBadge` — already in the component library
- `MetricCard` — reuse for website health score card
- `MetricCard` from `@/components/metric-card` — already imported in page.tsx

**Types:**
- `Website` interface matching backend `WebsiteRead`
- `WebsiteListResponse` matching backend `WebsiteList`

**Query key conventions to follow (established by prior slices):**
- `["websites", "list"]` for list query
- `["websites", id]` for single-item query
- `["crawls", "list"]` + optional `website_id` filter for crawl history

---

## Testing Requirements

**Backend tests (existing or verify):**
- `GET /api/v1/websites/` — smoke test (list returns 200, correct shape)
- `GET /api/v1/websites/{id}` — smoke test (200 with valid UUID, 404 with invalid)
- `GET /api/v1/crawls/?website_id={id}` — verify filtering works (if implemented)

**Frontend tests (add):**
- `apps/web/src/lib/queries/useWebsites.test.ts` — verify hook calls correct endpoint, returns parsed data
- `apps/web/src/lib/queries/useWebsite.test.ts` — verify hook calls correct endpoint with ID param
- `apps/web/src/app/businesses/page.test.tsx` — verify page renders website list from API, shows loading/error/empty states
- `apps/web/src/app/websites/[id]/page.test.tsx` — verify page renders website data + crawl history

**E2E (Playwright) — if available:**
- `tests/e2e/businesses.spec.ts` — navigate to /businesses, verify real API data renders
- `tests/e2e/website-detail.spec.ts` — navigate to /websites/[id], verify crawl history table

---

## Risks

1. **`GET /api/v1/crawls/` does not support `website_id` filter** — if the crawls router doesn't accept `website_id` as a query param, the website detail page will show all crawls and need client-side filtering. Fix: add `website_id: Query` param to `list_crawls` router (backend change — coordinate with Ryzen 9).

2. **Backend authentication placeholder** — `create_business` has a hardcoded `user_id = UUID("00000000-0000-0000-0000-000000000000")`. All backend queries are currently unauthenticated. If auth is added later, frontend hooks will need to handle JWT tokens. Keep this in mind; do not hardcode user_id in frontend.

3. **Website schema mismatch** — if `WebsiteRead` schema fields differ from what the frontend types expect, the `Website` TypeScript interface needs to be updated to match. Verify `services/api/schemas/website.py` against the planned TypeScript interface before wiring.

4. **Crawl creation endpoint missing** — the slice ends at triggering a crawl. The `POST /api/v1/crawls/` endpoint must exist and accept `{ website_id, crawl_type? }`. If it doesn't, that becomes a backend blocker for the next slice after this one.

5. **No website associated with a business** — the businesses page mock shows each business has 1 website, but the `Business` model may not have a direct `website_id` FK. The website detail page may need to go through `GET /api/v1/websites/?business_id=<id>` instead. Verify model relationships.

---

## Prompt For Ryzen 9

---

**Implementation Prompt: Websites API Wiring + Website Detail Page**

**Branch:** `feature/ryzen9-api-wiring-websites-detail`

**Base:** `feature/ryzen9-api-wiring-businesses-next` (commit `34f0e66`)

**Goal:** Wire `GET /api/v1/websites/` into the businesses page (replacing mock data), then create a website detail page at `/websites/[id]` that shows website info and crawl history.

**Step 1 — Inspect backend schemas before wiring**
Read `services/api/schemas/website.py` and `services/api/routers/websites.py` before writing any TypeScript. The frontend `Website` interface must match `WebsiteRead` field-for-field.

**Step 2 — Add TypeScript types**
Create `apps/web/src/lib/api/types/websites.ts`:
```typescript
export interface Website {
  id: string;
  business_id: string;
  url: string;
  name: string;
  created_at: string;
  updated_at: string;
}
export interface WebsiteListResponse {
  items: Website[];
  total: number;
}
```

**Step 3 — Add React Query hooks**
Create `apps/web/src/lib/queries/useWebsites.ts` (list, accepts optional `businessId` filter) and `apps/web/src/lib/queries/useWebsite.ts` (single item by ID). Follow the exact pattern from `useBusinesses.ts` and `useCrawls.ts`.

**Step 4 — Wire websites into /businesses page**
Replace the hardcoded `businesses` mock array in `apps/web/src/app/businesses/page.tsx` with `useWebsites()`. Show website name, URL, and a link to `/websites/{id}`. Preserve the Add Business button (mock, no backend needed yet).

**Step 5 — Create website detail page**
Create `apps/web/src/app/websites/[id]/page.tsx`:
- Fetch website by ID with `useWebsite(id)`
- Display website name, URL, created date
- Fetch crawl history with `useCrawls()` (filter client-side by `website_id` matching the current website)
- Render crawl history in a table (similar to Recent Crawls on dashboard): columns = Website ID (truncated), Status badge, Pages, When
- Add a "New Crawl" button (links to `/businesses` for now — crawl creation is a future slice; do NOT implement POST /crawls in this slice)
- Show loading/error/empty states for both the website fetch and crawl history

**Step 6 — Verify routes constant**
Confirm `WEBSITES` and `WEBSITE_BY_ID` exist in `apps/web/src/lib/api/routes.ts`. If not, add them following the existing pattern.

**Step 7 — Verify build**
```bash
cd apps/web && npm run build
```
Must succeed with no TypeScript errors.

**Step 8 — Verification**
Run `python scripts/verify_local.py` (or equivalent backend smoke). Run `pytest tests/ -q` to confirm backend still green.

**Do NOT:**
- Implement any POST/PATCH/DELETE mutations
- Change any backend files
- Add authentication handling
- Build the crawl creation modal/page (save for next slice)

---

## Prompt For Step Flash

---

**Verification Prompt: Websites API Wiring + Website Detail Page**

**Branch to verify:** `feature/ryzen9-api-wiring-websites-detail`

**Scope:** Review the complete diff from base (`34f0e66`) to the implementation branch. Verify the following checklist:

**1. Type correctness**
- [ ] `apps/web/src/lib/api/types/websites.ts` exists with `Website` and `WebsiteListResponse` interfaces
- [ ] `Website` fields match backend `WebsiteRead` from `services/api/schemas/website.py` exactly
- [ ] No `any` types used

**2. Hook correctness**
- [ ] `useWebsites(businessId?)` calls `apiGet` with `API_ROUTES.WEBSITES` (with optional `business_id` query param)
- [ ] `useWebsite(id)` calls `apiGet` with `API_ROUTES.WEBSITE_BY_ID(id)`
- [ ] Both use `@tanstack/react-query` `useQuery` with appropriate query keys
- [ ] No mutations (no `useMutation` anywhere)

**3. /businesses page wiring**
- [ ] Mock data removed from `apps/web/src/app/businesses/page.tsx`
- [ ] `useWebsites()` hook wired in
- [ ] Each business shows its associated website count/name with a link to `/websites/{id}`
- [ ] Add Business button preserved (can be a no-op/link)
- [ ] Loading, error, and empty states rendered

**4. Website detail page**
- [ ] `apps/web/src/app/websites/[id]/page.tsx` exists
- [ ] Uses `useWebsite(params.id)` to fetch website data
- [ ] Uses `useCrawls()` + client-side filter by `website_id` for crawl history
- [ ] "New Crawl" button present (links to `/businesses` as placeholder — no POST call)
- [ ] Loading, error, and empty states for both website and crawl history

**5. No backend changes**
- [ ] No files in `services/` modified
- [ ] No files in `tests/` modified (smoke tests still pass)

**6. Build verification**
- [ ] `cd apps/web && npm run build` passes with zero errors
- [ ] No TypeScript errors in the diff

**7. Working tree**
- [ ] Only the planned files changed; no accidental modifications
- [ ] No `.env` or secrets committed

**Report format:**
```
VERIFICATION RESULT: PASS / FAIL

Files reviewed:
- [list all changed files]

Checklist:
1. Type correctness: PASS/FAIL + notes
2. Hook correctness: PASS/FAIL + notes
3. /businesses page wiring: PASS/FAIL + notes
4. Website detail page: PASS/FAIL + notes
5. No backend changes: PASS/FAIL + notes
6. Build verification: PASS/FAIL + notes
7. Working tree clean: PASS/FAIL + notes

Issues found (if any):
[describe any problems]
```

If all checks pass, the slice is approved for merge into `feature/backend-phase2`.
