# Handoff: MTVSEO-AUDITS-PAGE-REALDATA-001-MrR9

## What Changed

Replaced all hardcoded/mock data in `apps/web/src/app/audits/page.tsx` with real API-backed SEO issue data from `useSeoIssues()`.

## Mock/Static Data Removed

| Static/Fake Item             | Removed | Replacement |
| ---------------------------- | ------- | ----------- |
| Hardcoded issues array (9 items) | yes | `useSeoIssues()` API data |
| Hardcoded score breakdown (82, 90, 61, etc.) | yes | Real severity counts from API |
| Hardcoded mtvhvac.com domain | yes | Removed entirely |
| Fake "Last run: 2 hours ago" | yes | Removed; total count shown instead |
| Mock scoreBreakdown array | yes | Issue breakdown by severity (count only) |

## Real Data Now Wired

- **Hook used**: `useSeoIssues()` from `@/lib/queries/useSeoIssues`
- **API endpoint**: `/api/v1/seo-issues/`
- **Displayed fields**: `title`, `issue_type`, `severity`, `affected_element`, `created_at`
- **Metrics computed from real data**:
  - Total issue count from `data.total`
  - Severity breakdown counts (critical/high/medium/low/info) computed by iterating `data.items`
- **No fake audit score** — the old "Score Breakdown" (Crawlability 82, Indexability 90, etc.) had no backend equivalent and has been removed. The new breakdown shows real issue counts by severity.

## States Handled

- **Loading**: Skeleton pulse animation for issue counts; "Loading issues..." for the table
- **Error**: Red alert icon + "Failed to load SEO issues. Check that the backend is running."
- **Empty (all)**: CheckCircle2 icon + "No SEO issues found. Run a crawl to start discovering issues."
- **Empty (filtered)**: "No [severity] severity issues."

## What Was Intentionally Removed

- `scoreBreakdown` fake scores: No backend field provides per-category audit scores
- Domain name `mtvhvac.com`: No single "current domain" field exists on the backend; showing a domain requires selecting a specific website/business first
- Fake "Last run" timestamp: No audit-run timestamp exists on the backend SEO issue model; `created_at` on individual issue records is the issue-creation time, not an audit run time

## Verification

| Check | Result |
| ----- | ------ |
| git status | clean |
| python scripts/verify_local.py | pass |
| pytest tests/ -q | 40 passed |
| python -m compileall | pass |
| npm install && npm run build (apps/web) | pass |
| grep mtvhvac.com in audits/ | none |
| grep "Last run\|2 hours ago" in audits/ | none |
| grep mock/fake in audits/ | only my own explanatory comment |

## Branch & Commit

- Branch: `feature/audits-page-realdata-001`
- Base commit: `87051af3b39297aac9bc6953aedc73988093e21d`
- Final commit: `73e001f`
- Pushed: yes

## Next Step for Mr.R7

Verify at commit `73e001f` on branch `feature/audits-page-realdata-001`. No backend changes were made; no migration needed.