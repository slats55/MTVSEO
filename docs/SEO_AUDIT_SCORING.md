# SEO Audit Scoring — Autonomous SEO Agent OS

**Status:** Phase 2 — Implementation in `packages/seo_audit/scorer.py`

---

## Overview

Technical SEO score is a 0–100 weighted sum across categories. Sub-scores range 0–category_max.

### Weights

| Category | Weight |
|----------|--------|
| Crawlability | 20 |
| Indexability | 20 |
| Metadata / On-page | 15 |
| Architecture / Internal Links | 15 |
| Performance / Mobile / Accessibility | 15 |
| Structured Data | 10 |
| Security / Trust | 5 |

Total: 100 points.

---

## Algorithm

1. Start each category at its maximum (weight).
2. Subtract penalties for issues found in that category.
3. Scale penalties by:
   - Issue severity (critical > high > medium > low > info)
   - Number of affected pages (relative to pages crawled)
4. Apply bonuses for good practices (schema coverage, indexability, low error rate).
5. Cap each category at its max (never go negative).

---

## Severity Penalties

Base penalty per issue (before scaling):

| Severity | Crawl | Index | Meta | Arch | Perf | Schema | Sec |
|----------|-------|-------|------|------|------|--------|-----|
| Critical | 8 | 8 | 6 | 6 | 6 | 4 | 3 |
| High | 5 | 5 | 4 | 4 | 4 | 3 | 2 |
| Medium | 3 | 3 | 2 | 2 | 2 | 1 | 1 |
| Low | 1 | 1 | 1 | 1 | 1 | 0.5 | 0.5 |

Penalty per issue = base_penalty * scale_factor

Scale factor = `min( (affected_pages / pages_crawled * 10), 3.0 )` when pages_crawled > 0, else 1.0.

Category penalty never exceeds category max.

---

## Bonuses

- **Structured Data**: +2 pts if ≥80% pages have schema; +1 pt if ≥50%
- **Indexability**: +2 pts if ≥90% pages indexable; +1 pt if ≥75%
- **Crawlability**: +2 pts if ≤1% error rate (4xx/5xx); +1 pt if ≤5%

Bonuses are additive within category limits.

---

## Grade Mapping

Total score → grade:

- 90–100: A (Excellent)
- 80–89: B (Good)
- 65–79: C (Fair)
- 50–64: D (Poor)
- 0–49: F (Critical)

---

## Usage

```python
from packages.seo_audit.scorer import compute_score

score = compute_score(
    issues=audit_issues,
    pages_discovered=crawl_summary.pages_discovered,
    pages_crawled=crawl_summary.pages_crawled,
    pages_with_schema=pages_with_schema_count,
    pages_indexable=pages_indexable_count,
    pages_4xx=pages_4xx_count,
    pages_5xx=pages_5xx_count,
    homepage_has_schema=homepage_has_org_schema,
)
```

---

*Last updated:* 2025-05-07
*Branch:* `feature/backend-phase2`