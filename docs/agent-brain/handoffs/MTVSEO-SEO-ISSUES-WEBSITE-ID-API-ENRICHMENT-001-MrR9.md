# Handoff: MTVSEO-SEO-ISSUES-WEBSITE-ID-API-ENRICHMENT-001

**Agent:** Mr.R9  
**Task ID:** MTVSEO-SEO-ISSUES-WEBSITE-ID-API-ENRICHMENT-001  
**Original branch:** `feature/audits-website-crawl-links-001`  
**Base:** `origin/feature/backend-phase2`  
**Reframed from:** MTVSEO-AUDITS-WEBSITE-CRAWL-LINKS-001  

---

## Summary

Add `website_id` to SEO issue API responses via existing `page → crawl_run → website` relationship, enabling the frontend audits page to link audit rows to real website detail pages. No DB migration, no new DB columns.

---

## Branch Status

| Item | Value |
|------|-------|
| Starting commit (de828fe) | `feat: link audits to website and crawl details` |
| Post-repair commit | (to be created) |
| Base check | BASED_ON_BACKEND_PHASE2 ✓ |

---

## Files Changed

### Backend (3 files)
- `services/api/schemas/seo_issue.py` — `website_id: UUID → UUID | None = None`
- `services/api/routers/seo_issues.py` — replaced zero UUID fallback with `None`; fixed missing EOF newline
- (no new migration files)

### Frontend (2 files)
- `apps/web/src/lib/api/types/seo_issues.ts` — `website_id: string → website_id?: string | null`
- `apps/web/src/app/audits/page.tsx` — simplified guard from `!!website_id && !== zero UUID` to `!!website_id`

### Unchanged (no new files)
- No DB migration added
- No new DB column
- No migration required

---

## Key Repair: Zero UUID → Nullable

### What the original branch did
```python
website_id = UUID("00000000-0000-0000-0000-000000000000")  # zero UUID fallback
```

### What the repair does
```python
website_id: UUID | None = None
```

**Why nullable is safe:**
- Frontend guards with `!!issue.website_id` — no link rendered when null
- Backend derives `website_id` only from existing relationships (no fake data invented)
- No DB schema change — Pydantic `UUID | None = None` is purely in the API layer
- If the relationship chain is broken for a given SEO issue, the API simply omits the website link rather than faking one

---

## website_id Derivation Chain

```
SeoIssue.page (page_id FK)
  → Page.crawl_run (crawl_run FK)
    → CrawlRun.website (website FK)
      → Website.id  ← exposed as website_id in SeoIssueRead
```

The chain is loaded via SQLAlchemy `joinedload` in both `list_seo_issues` and `get_seo_issue`.

---

## Endpoints Affected

| Endpoint | Effect |
|----------|--------|
| `GET /api/v1/seo-issues/` | Now returns `website_id: UUID | null` per item |
| `GET /api/v1/seo-issues/{id}` | Now returns `website_id: UUID | null` |

Both are additive / backward-compatible — existing clients ignoring `website_id` are unaffected.

---

## Verification Results

| Check | Result |
|-------|--------|
| `python scripts/verify_local.py` | ✓ ALL CHECKS PASSED |
| `pytest tests/ -q` | ✓ 40 passed in 2.30s |
| `python -m compileall` | ✓ Clean |
| `npm run build` (apps/web) | ✓ Build successful |
| Fake-data grep | ✓ Zero-UUID removed from seo_issues; only pre-existing placeholder in `businesses.py` (unrelated file) |
| Artifact check | ✓ NO_BUILD_ARTIFACT |

---

## Fake-Data Notes

The grep hit `services/api/routers/businesses.py:67` with a pre-existing zero UUID used as an auth-context placeholder. This is **not** part of this branch's changes and existed before this task.

No fake `seoScore`, `geoScore`, mock websites, mock crawls, or mock issues were introduced by this branch.

---

## Commit Plan

```
git add .
git commit -m "fix: use nullable website_id instead of zero UUID fallback"
git push origin feature/audits-website-crawl-links-001
```

---

## Recommendation

**READY_FOR_R7** — the branch is based on `origin/feature/backend-phase2`, makes only additive API enrichment changes, uses nullable `website_id` per Myles's preference, and passes all backend and frontend checks.

---

**Tagged:** [@Mr.R7](mention://agent/4a8d5b28-b7b0-485b-8237-775306a8d020) — please verify independently per Phase 3 of the morning control prompt.
