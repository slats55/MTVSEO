# Ryzen 9 Businesses API Wiring

## Purpose
Second frontend API wiring slice. Targets read-only `GET /api/v1/businesses/` wiring to the dashboard. No mutations, no create/update/delete flows. Establishes patterns for subsequent slices (websites, pages).

## Branch Context
- **Base branch:** `feature/backend-phase2`
- **Base commit:** `c93886d` ("docs: verify post-merge crawls API wiring")
- **Implementation branch:** `feature/ryzen9-api-wiring-businesses-next`

## Endpoint Wired
- `GET /api/v1/businesses/` — list all businesses accessible to the current user

**Response shape:**
```json
{
  "items": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "name": "string",
      "website_url": "string | null",
      "description": "string | null",
      "business_type": "string | null",
      "location": "string | null",
      "phone": "string | null",
      "email": "string | null",
      "is_cannabis": false,
      "is_ymyl": false,
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": 0
}
```

## Files Changed

| File | Change |
|------|--------|
| `apps/web/src/lib/api/routes.ts` | BUSINESSES constant already existed — no change needed |
| `apps/web/src/lib/api/types/businesses.ts` | **Created** — TypeScript `Business` and `BusinessListResponse` types |
| `apps/web/src/lib/queries/useBusinesses.ts` | **Created** — React Query hook for `GET /api/v1/businesses/` |
| `apps/web/src/app/page.tsx` | **Modified** — added `useBusinesses` import; added Business Projects panel; renamed crawl state vars for clarity |
| `docs/RYZEN9_BUSINESSES_API_WIRING.md` | **Created** — this document |

## Behavior Added

### business route constant
`BUSINESSES: "/api/v1/businesses/"` — already existed in `routes.ts` from prior wiring plan. No change needed.

### business API types
`apps/web/src/lib/api/types/businesses.ts`:
- `Business` interface — mirrors backend `BusinessRead` field-for-field (string UUIDs)
- `BusinessListResponse` — `{ items: Business[], total: number }` matches backend `BusinessList`

### useBusinesses hook
`apps/web/src/lib/queries/useBusinesses.ts`:
- Calls `apiGet<BusinessListResponse>(API_ROUTES.BUSINESSES)`
- React Query `useQuery` with `["businesses", "list"]` query key
- Returns `{ data, isLoading, isError }`
- No mutations, no auth assumptions

### dashboard Business Projects panel
New section above "Two Column Layout" on dashboard:
- **Loading state:** centered text "Loading businesses..."
- **Error state:** centered text "Failed to load businesses" (red)
- **Empty state:** Building2 icon + "No businesses yet." + "Create one from the Businesses page."
- **Data state:** up to 4 businesses listed with name, location/business_type, website URL, cannabis/YMYL badges

### existing crawls wiring preserved
- `useCrawls` hook unchanged
- Recent Crawls table unchanged
- All states (loading/error/empty/fallback mock) preserved
- State vars renamed to `crawlData`/`crawlLoading`/`crawlError` to avoid collision with new `businessData`/`bizLoading`/`bizError`

## Backend Safety
- No backend files modified
- No backend tests modified
- No API contract changed (read-only GET)
- No mutations added (no POST/PUT/PATCH/DELETE anywhere)

## Environment
- `NEXT_PUBLIC_API_URL` from `process.env` reused (existing `client.ts` behavior unchanged)
- `.env.local` — NOT committed (already in `.gitignore`)

## Verification Results

### npm install + build (apps/web)
```
cd apps/web && npm install && npm run build
```
Result: **PASS** (see build output in task report)

### python scripts/verify_local.py
Result: **ALL CHECKS PASSED**

### pytest tests/ -q
Result: **34 passed in 1.96s**

### python -m compileall services packages tests
Result: **Clean compile — no syntax errors**

### Forbidden mutation check
```
grep -R "POST\|PUT\|PATCH\|DELETE" -n apps/web/src
```
Result: **No mutations found in frontend src**

### .env.local check
```
find apps/web -name ".env.local" -print
```
Result: **No .env.local found (not tracked)**

## Known Limitations
- **No business create/update/delete yet** — mutations not wired; no business detail page
- **No auth/session filtering** — backend returns all businesses; no user-scoped filtering on frontend
- **No websites wiring yet** — next slice after Step Flash review
- **No full business management page** — only a read-only panel on dashboard
- **No pagination controls** — `useBusinesses` fetches full list (no limit/skip params)
- **No website_name in business list** — UI shows location/business_type but no website name (backend doesn't JOIN to website table)

## Recommended Next Step
1. Step Flash reviews `feature/ryzen9-api-wiring-businesses-next`
2. If clean, merge into `feature/backend-phase2`
3. Next slice: websites API wiring (`GET /api/v1/websites/`) — wire website overview panel on dashboard similar to this slice
