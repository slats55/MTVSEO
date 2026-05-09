# Ryzen 9 Websites API Wiring Readiness Audit

## Purpose

This audit assesses readiness for the next frontend API wiring slice: `GET /api/v1/websites/`. It follows the crawls wiring implementation on `feature/ryzen9-api-wiring-crawls-first` and prepares the foundation for Step Flash's next implementation branch.

---

## Branch Context

- **Base branch:** `feature/backend-phase2`
- **Base commit:** `415587a` ("Merge frontend API wiring plan docs")
- **Audit branch:** `audit/ryzen9-websites-api-wiring-readiness`
- **Crawls wiring branch status:** `feature/ryzen9-api-wiring-crawls-first` — commit `41f5fb8` pushed, pending Step Flash review and merge. Do not implement websites wiring until crawls branch is reviewed.

---

## Baseline Verification

```
python scripts/verify_local.py               ✓ ALL CHECKS PASSED
pytest tests/                                 ✓ 34 passed (0 failed)
python -m compileall services packages tests  ✓ no errors
```

---

## Website Endpoint Review

### GET /api/v1/websites/

**Router:** `services/api/routers/websites.py`

**Query parameters:**
- `business_id: UUID | None` — filter by business (optional)
- `skip: int = 0` — pagination offset
- `limit: int = 20` — pagination limit (max 100)

**Response shape (`WebsiteList`):**
```json
{
  "items": [
    {
      "id": "uuid",
      "business_id": "uuid",
      "url": "https://example.com",
      "name": "Example Site",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 42
}
```

**Sorting:** `created_at desc` (server-side)

**Empty state:** `{"items": [], "total": 0}` — clean empty array, no error

**Auth:** No user filtering — returns all websites (auth/productization deferred)

### GET /api/v1/websites/{website_id}

**Response:** Single `WebsiteRead` object

**404 behavior:** Returns `{"detail": "Website with id=<uuid> not found"}`

### POST /api/v1/websites/

**Requires:** `business_id` UUID must reference an existing Business

**Request body:**
```json
{
  "business_id": "uuid",
  "url": "https://example.com",
  "name": "Example Site" // optional
}
```

**Not in scope for this slice** — read-only wiring only

### PATCH /api/v1/websites/{website_id}

**Partial update** — not in scope

### DELETE /api/v1/websites/{website_id}

**204 no content** — not in scope

---

## Dashboard Mapping

### Where Website Data Connects to Dashboard

The current `apps/web/src/app/page.tsx` has hardcoded project/website context:

1. **Business selector in top nav** — shows "MTV Tech Solutions" as hardcoded string. Needs real business context from `GET /api/v1/businesses/`.

2. **Active website context** — no active website selection exists yet in the dashboard. This is a future state management concern.

3. **Recent Crawls website_id display** — the crawls wiring branch (`feature/ryzen9-api-wiring-crawls-first`) currently displays truncated `website_id` UUID in the Recent Crawls table. Once the websites wiring branch merges and a website lookup map is available client-side, the `website_id` can be replaced with the actual website `name` or `url`.

4. **Score cards (deferred)** — no score data is currently available from any endpoint, so KPI cards remain mock data. This is not unblocked by websites wiring.

### Recommended Wire Order

1. **Phase A (after crawls merge):** Wire `useWebsites()` to fetch websites on mount. Display first website's `name` as the active project context label in the nav. Show total count.

2. **Phase B:** After Phase A is stable, create a client-side `Map<website_id, WebsiteRead>` from the fetched websites. Pass this map to the Recent Crawls table to replace `website_id` UUID display with `name` or `url`.

---

## Recommended Next Implementation Slice

Branch name: `feature/stepflash-api-wiring-websites-next`

This branch should ONLY add read-only website wiring. No mutations.

### Files to add:

```
apps/web/src/lib/api/types/websites.ts    (NEW — Website, WebsiteList types)
apps/web/src/lib/queries/useWebsites.ts    (NEW — useWebsites hook)
```

### Files to modify:

```
apps/web/src/lib/api/routes.ts             (add WEBSITES and WEBSITE_BY_ID)
apps/web/src/app/page.tsx                  (wire project context from websites)
```

### Implementation details:

**`apps/web/src/lib/api/types/websites.ts`:**
```typescript
export interface Website {
  id: string;
  business_id: string;
  url: string;
  name: string | null;
  created_at: string;
  updated_at: string;
}

export interface WebsiteListResponse {
  items: Website[];
  total: number;
}
```

**`apps/web/src/lib/queries/useWebsites.ts`:**
```typescript
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type { WebsiteListResponse } from "@/lib/api/types/websites";

export function useWebsites(businessId?: string) {
  const params = businessId ? `?business_id=${businessId}` : "";
  return useQuery<WebsiteListResponse>({
    queryKey: ["websites", { businessId }],
    queryFn: () => apiGet<WebsiteListResponse>(`${API_ROUTES.WEBSPITES}${params}`),
  });
}
```

**Dashboard wiring (`page.tsx`):**
- Add `useWebsites()` hook
- Display first website's `name` (or `url` if `name` is null) in the business selector button as a temporary live label
- Show loading/error/empty states consistent with the crawls pattern
- Keep "MTV Tech Solutions" as fallback until real business data is wired

**Optional enhancement (only if crawls branch has merged):**
- After `useWebsites()` returns, build a `Map<website_id, Website>` from `items`
- Pass this map to the Recent Crawls section so `website_id` UUID display can be replaced with `website.name` or `website.url`

---

## Risks / Caveats

1. **No auth/user ownership** — `GET /api/v1/websites/` returns all websites with no user filter. Fine for local dev; needs auth work before production. Do not wire user-specific data yet.

2. **No selected-website state** — the dashboard has no concept of "selected website." The nav business selector is hardcoded. Website wiring should start with display-only; selection state management is a future slice.

3. **Crawl rows still show website_id** — the crawls wiring branch displays truncated UUIDs. This can be improved client-side after websites are fetched (no backend change required), but the enrichment logic is optional and can be deferred.

4. **No website_id → name join in backend** — `CrawlRunRead` does not include `website_name`. The frontend must do the join client-side via a `Map` once websites are available. This is a known deferred enhancement; the crawls branch handles it by showing the UUID prefix.

5. **Empty database** — if no websites exist, `useWebsites()` returns `items: []` cleanly. The UI should show empty state gracefully and fall back to hardcoded label.

6. **CORS** — same as crawls slice: `NEXT_PUBLIC_API_URL=http://localhost:8000`, use `localhost` not `127.0.0.1`.

7. **`name` is optional in backend** — `WebsiteCreate.name` is `str | None`. The UI should handle `null` gracefully by falling back to the `url`.

---

## Dependency Notes

**CRITICAL: Do not implement websites wiring until Step Flash reviews and merges `feature/ryzen9-api-wiring-crawls-first` (commit `41f5fb8`).**

Rationale:
- The websites wiring branch will be based on the same `feature/backend-phase2` commit that the crawls branch is merged into.
- If the crawls branch requires fixes, the base code will change and the websites branch will need rebase/diff.
- The crawls branch is the pattern/template for websites wiring — following the same file structure (`types/`, `queries/`, `routes.ts` update, `page.tsx` wiring) is easier after the crawls branch has been confirmed working.

---

## Crawls Branch Inspection

The following files were successfully inspected from `origin/feature/ryzen9-api-wiring-crawls-first`:

- `docs/RYZEN9_CRAWLS_API_WIRING.md` — confirmed file exists and describes the wiring pattern
- `apps/web/src/lib/api/types/crawls.ts` — confirmed `CrawlStatus`, `CrawlRun`, `CrawlListResponse` types
- `apps/web/src/lib/queries/useCrawls.ts` — confirmed `useQuery` pattern using `apiGet`, `API_ROUTES`, and typed response

The websites wiring should follow the same pattern exactly:
1. `types/websites.ts` mirrors `types/crawls.ts` structure
2. `useWebsites.ts` mirrors `useCrawls.ts` pattern (read-only `useQuery`, no mutations)
3. `routes.ts` already has `WEBSITES` entry — just confirm it
4. `page.tsx` wiring follows same loading/error/empty/mock-fallback pattern

---

## Final Verdict

**READY AFTER CRAWLS MERGE**

The backend is fully ready for websites wiring. All endpoints return clean JSON with proper error responses. The frontend pattern is established by the crawls branch. The next implementation branch (`feature/stepflash-api-wiring-websites-next`) can be created as soon as `feature/ryzen9-api-wiring-crawls-first` is merged into `feature/backend-phase2` and Step Flash has reviewed the pattern.

Key pre-conditions before starting websites wiring:
1. Step Flash merges `feature/ryzen9-api-wiring-crawls-first`
2. `python scripts/verify_local.py && pytest tests/ -q` passes on `feature/backend-phase2` after merge
3. `apps/web/` build is clean on `feature/backend-phase2` post-merge
4. Base commit is confirmed to be `415587a` or whatever `HEAD` of `feature/backend-phase2` becomes after crawls merge