# Handoff: MTVSEO-BUSINESSES-REALDATA-002
**Agent**: Mr.R9
**Task ID**: MTVSEO-BUSINESSES-REALDATA-002
**Status**: COMPLETE

---

## 1. TASK ID

`MTVSEO-BUSINESSES-REALDATA-002`

## 2. BRANCH

- **Feature branch**: `feature/businesses-page-realdata-002`
- **Base**: `origin/feature/backend-phase2`
- **Base commit**: `8290db7 merge: dashboard real-data stabilization`

## 3. PURPOSE

Remove hardcoded mock/fake business data from the Businesses page (`apps/web/src/app/businesses/page.tsx`) and wire it to the real Businesses API using the existing `useBusinesses()` hook and `Business` types.

---

## 4. FILES CHANGED

| File | Change |
| ---- | ------ |
| `apps/web/src/app/businesses/page.tsx` | Complete rewrite: replaced hardcoded `const businesses = [...]` array with `useBusinesses()` hook; added loading/error/empty states; adapted UI to real API fields |
| `docs/agent-brain/handoffs/MTVSEO-BUSINESSES-REALDATA-002-MrR9.md` | This handoff document |

---

## 5. MOCK/FAKE DATA REMOVED

### User-facing mock business data found:
- `const businesses = [...]` — hardcoded array of 3 fake businesses:
  - `"MTV Tech Solutions"` / `mtvhvac.com` / Home Services — HVAC
  - `"Green Culture"` / `green-culture.co` / Cannabis — Retail
  - `"Country Roads Car Services"` / `countryroadsauto.com` / Automotive — Car Services
- Hardcoded SEO score values (`72`, `61`, `null`)
- Hardcoded last crawl times (`"2h ago"`, `"1d ago"`, `"2d ago"`)
- Hardcoded website counts (`1`)

### Removed:
- All 3 hardcoded business rows
- `seoScore`, `lastCrawl`, `websites` hardcoded fields from mock objects
- `domain` and `industry` fields from mock objects (real API uses `website_url` and `business_type`)

### Remaining test-only mock data:
- No mock data remains in the businesses page component
- Other pages (`/audits`, `/reports`) do not use mock data

### Concerns:
- None. The mock data was only in `apps/web/src/app/businesses/page.tsx`.

---

## 6. REAL DATA SOURCE USED

- **Hook**: `useBusinesses()` from `apps/web/src/lib/queries/useBusinesses.ts`
- **Route**: `GET /api/v1/businesses/` (from `API_ROUTES.BUSINESSES`)
- **Types**: `Business` / `BusinessListResponse` from `apps/web/src/lib/api/types/businesses.ts`
- **API contract**: `{ items: Business[], total: number }` — aligned with backend `BusinessList` Pydantic schema

---

## 7. BUSINESSES PAGE STATE BEHAVIOR

| State | Behavior |
| ----- | -------- |
| **Loading** | Centered "Loading businesses..." text in slate-500, centered in the list area |
| **Error** | Centered "Failed to load businesses." in red-400 |
| **Empty** | Centered `Building2` icon + "No businesses yet." + "Add a business to get started." |
| **Data loaded** | Maps `data.items` to business rows. Shows name, website_url, business_type/location as industry. Shows Cannabis/YMYL badges when set. SEO Score and Last Crawl show `—` (no API endpoint for these yet). |
| **Add Business button** | Disabled with tooltip "Create flow coming soon" — no create page exists yet |

### Real API fields displayed:
- `name` → business name
- `website_url` → domain (shown with Globe icon)
- `business_type` or `location` → industry context
- `is_cannabis` → Cannabis badge
- `is_ymyl` → YMYL badge

### Fields not available from Business API (shown as `—`):
- SEO Score (no scoring endpoint)
- Last Crawl (not on Business model)
- Number of websites (requires a separate aggregation — not currently surfaced)

---

## 8. VERIFICATION RESULTS

| Check | Result | Notes |
| ----- | ------ | ----- |
| `python scripts/verify_local.py` | ✅ PASS | All 7 sections green |
| `pytest tests/ -q` | ✅ PASS | 40 passed in 2.36s — unchanged |
| `python -m compileall services packages tests scripts` | ✅ PASS | No errors |
| `cd apps/web && npm install && npm run build` | ✅ PASS | Route /businesses 1.97 kB, TypeScript + build clean |
| Fake/mock grep (`MTV Tech\|Green Culture\|businesses =`) | ✅ PASS | No hardcoded mock data found |

---

## 9. KNOWN LIMITATIONS

1. **Add Business button disabled** — no create page exists yet. The button is visually present but disabled with "Create flow coming soon" tooltip. This is honest and correct behavior.

2. **SEO Score shows `—`** — the Business model has no SEO score field. A scoring system or summary endpoint would need to be added separately.

3. **Last Crawl shows `—`** — `CrawlRun` is linked to `Website`, not directly to `Business`. A business-level summary of the most recent crawl would require a new aggregation query.

4. **Number of websites shows `—`** — `Business` has no direct website count. This could be computed by linking websites by `business_id`, but no dedicated endpoint exists yet.

5. **Search input is non-functional** — the search bar is present but filters nothing since there is no client-side filtering implemented and the API does not support search params. This matches the original design and is not a regression.

6. **No pagination controls** — the `useBusinesses()` hook fetches the full list with `limit=20` (backend default). No load-more or paginated controls added.

---

## 10. HANDOFF TO MR.R7

**QA Verification Checklist**:

1. **Confirm mock data is gone**:
   ```bash
   grep -n "MTV Tech Solutions\|Green Culture\|Country Roads\|businesses =" apps/web/src/app/businesses/page.tsx
   ```
   Should return no matches.

2. **Confirm the page renders loading/error/empty states**:
   - Backend off → should show "Failed to load businesses."
   - Backend on, no businesses → should show empty state with Building2 icon
   - Backend on, businesses exist → should render real data

3. **Confirm API wiring**:
   - Network tab should show `GET /api/v1/businesses/` called when the page loads
   - Response should be `{ items: [...], total: N }`

4. **Confirm Add Business button is disabled**:
   - Button should be visually muted with tooltip "Create flow coming soon"

5. **Run the full test suite**:
   ```bash
   .venv/bin/python -m pytest tests/ -q
   ```
   All 40 tests should still pass.

6. **Run frontend build**:
   ```bash
   cd apps/web && npm install && npm run build
   ```
   Should complete without TypeScript or build errors.

---

## 11. HANDOFF TO MR.M1

**Pre-merge gate checklist**:

1. **Base commit confirmed**: `8290db7 merge: dashboard real-data stabilization` — matches the assigned base.

2. **No regressions to existing functionality**:
   - Dashboard (`page.tsx`) still uses `useBusinesses()`, `useWebsites()`, `useCrawls()`, `useSeoIssues()` with real API data — this change does not touch it.
   - All 40 tests pass.

3. **Scope was contained**:
   - Only `apps/web/src/app/businesses/page.tsx` was modified.
   - No backend changes, no new endpoints, no auth changes.
   - No mock data introduced.

4. **No fake data added**:
   - SEO Score, Last Crawl, Website count show `—` honestly rather than fake values.
   - Add Business button is disabled rather than fake-linked.

5. **Verification complete**: All checks pass (see section 8).

**Feature branch**: `feature/businesses-page-realdata-002`
**Last commit on branch**: (pending — will be pushed after review)
**Files changed**: 2 (1 page file + 1 handoff doc)

Ready for Step Flash review.
