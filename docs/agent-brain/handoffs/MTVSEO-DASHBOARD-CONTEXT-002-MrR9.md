# MTVSEO-DASHBOARD-CONTEXT-002 — Builder Handoff
**From:** Mr.R9  
**To:** Mr.R7 (QA), Mr.M1 (Review/Merge)  
**Task ID:** MTVSEO-DASHBOARD-CONTEXT-002  
**Branch:** `feature/dashboard-context-002-real-context`  
**Base Commit:** `a0ff73a` (merge: businesses page real-data wiring)  
**Latest Commit:** `37e1968` (fix(frontend): replace static dashboard context text)  
**Status:** COMPLETE  

---

## PURPOSE

Remove remaining hardcoded/static dashboard context text from the main dashboard page and replace with honest real-data or neutral behavior.

---

## FILES CHANGED

| File | Change |
| ---- | ------ |
| `apps/web/src/app/page.tsx` | Removed hardcoded "MTV Tech Solutions" from header subtext; replaced with first real business name from `useBusinesses()` hook, or neutral "SEO Dashboard Overview" fallback. Removed "Last sync: 5 min ago" static text. |
| `apps/web/src/app/layout.tsx` | Replaced hardcoded "MTV Tech Solutions" in business selector button with neutral "All Businesses" label. |

---

## OLD STATIC TEXT REMOVED

| Static Item | Old Behavior | New Behavior |
|---|---|---|
| Dashboard header subtext | `Overview for <span className="text-blue-400 font-medium">MTV Tech Solutions</span>` | If real businesses exist: `Overview for <first business name>`. If no businesses: `SEO Dashboard Overview`. |
| Dashboard sync timestamp | `Last sync: 5 min ago` | Removed entirely. No real sync concept exists; removed fake data. |
| Layout business selector | `MTV Tech Solutions` | `All Businesses` — neutral, no hardcoded account context. |

---

## NEW BEHAVIOR

**Business name in dashboard header:**
- Uses existing `useBusinesses()` hook (already on the page).
- If `businessData?.items` has at least one entry, displays the first business's `name`.
- If zero businesses exist (empty list), displays neutral `"SEO Dashboard Overview"`.
- Does not invent a business name.

**Sync text:**
- Removed `Last sync: 5 min ago` — no real sync timestamp concept exists in the app.
- The Refresh button remains; no replacement text added.

**Layout header business selector:**
- Changed from `MTV Tech Solutions` to `All Businesses`.
- This is a neutral placeholder; actual business switching logic is out of scope for this slice.

---

## DATA SOURCE / HONEST STATE

- Business name: `businessData.items[0].name` from `useBusinesses()` hook (real API via `/api/v1/businesses`).
- No businesses: neutral fallback text `"SEO Dashboard Overview"`.
- Sync: removed (no real sync timestamp exists).
- Layout selector: neutral `"All Businesses"` with span `id="layout-business-name"`.

---

## VERIFICATION RESULTS

| Check | Result | Notes |
|---|---|---|
| `python3 -m compileall services packages tests scripts` | PASS | No Python syntax errors. |
| `cd apps/web && npm install && npm run build` | PASS | Next.js build successful, all routes compile. |
| Static/fake text grep (`MTV Tech Solutions`, `Last sync: 5 min ago`) | PASS | No matches in active user-facing source code. |
| Dashboard real-data panels (crawls, businesses, websites, SEO issues) | INTACT | Previous MTVSEO-DASHBOARD-REALDATA-002 fix remains in place. |
| Businesses page real-data wiring | INTACT | Previous MTVSEO-BUSINESSES-REALDATA-002 fix remains in place. |
| Git pushed | PASS | Branch pushed to origin. |

---

## KNOWN LIMITATIONS

1. **Layout selector does not read real business data.** The layout.tsx file would need a context provider or client-side hook to read from `useBusinesses()` to show the actual selected business name. That is a larger refactor (needs layout-level state management or a context). This slice used neutral "All Businesses" to avoid false context.
2. **No sync timestamp implementation.** The issue explicitly forbids adding a metrics/sync endpoint in this slice. The "Last sync" text was removed because it was fake.
3. **No KPI cards or keyword opportunities restored.** These remain removed per the previous stabilization work.

---

## HANDOFF TO MR.R7 (QA)

Please verify:

1. `grep -R "MTV Tech Solutions" apps/web/src/` — should return no matches.
2. `grep -R "Last sync" apps/web/src/` — should return no matches.
3. Load the dashboard page — the header should show either a real business name (if businesses exist in the DB) or "SEO Dashboard Overview" (if no businesses).
4. The sync timestamp text should be gone from the dashboard header.
5. The layout header business selector should say "All Businesses", not "MTV Tech Solutions".
6. Run `cd apps/web && npm run build` — should pass.
7. Confirm previous real-data fixes (dashboard panels, businesses page) remain intact.

---

## HANDOFF TO MR.M1 (Review/Merge)

Please review:

1. Branch: `feature/dashboard-context-002-real-context`
2. Base: `origin/feature/backend-phase2` at `a0ff73a`
3. Latest commit: `37e1968`
4. Changes are minimal and surgical — only removes fake text and replaces with honest real-data or neutral fallback.
5. No new fake data introduced.
6. No backend changes.
7. Build passes.
8. PR can be opened against `feature/backend-phase2`.

---