# GEO Audit Scoring — Autonomous SEO Agent OS

**Status:** Phase 2 — Implementation in `packages/geo_audit/scorer.py`

---

## Overview

GEO/AI visibility score measures how well content can be cited by AI systems (ChatGPT, Claude, Perplexity). Range: 0–100 with weighted categories.

### Weights

| Category | Weight | Description |
|----------|--------|-------------|
| AI Crawler Access | 15 | Are friendly AI bots allowed in robots.txt? |
| Entity Clarity | 15 | Is the business clearly defined with schema + sameAs? |
| Citability | 25 | Can AI cite this page as a direct source? |
| AI Answer Readiness | 20 | Does content answer questions with sufficient depth? |
| Schema Markup | 10 | Is structured data present and correct? |
| LLM Readability | 5 | Is llms.txt present and well-structured? |

Total: 100 points.

---

## Algorithm

Same structure as SEO scoring:

1. Start each category at its maximum.
2. Apply penalties for issues found in that category based on severity and page count.
3. Add bonuses for good practices.
4. Cap each category at its max.

---

## Severity Penalties

Base penalty per issue (before scaling):

| Severity | AI Access | Entity | Citability | Readiness | Schema | LLM Read |
|----------|-----------|--------|-----------|-----------|--------|----------|
| Critical | 6 | 6 | 10 | 8 | 4 | 3 |
| High | 4 | 4 | 6 | 5 | 3 | 2 |
| Medium | 2 | 2 | 4 | 3 | 1.5 | 1 |
| Low | 1 | 1 | 2 | 1 | 0.5 | 0.5 |

Scale factor = `min( (affected_pages / pages_crawled * 10), 3.0 )` when pages_crawled > 0, else 1.0.

---

## Bonuses

- **Entity Clarity**: +3 pts if homepage has Organization schema (capped at category max)
- **LLM Readability**: +2 pts if llms.txt is found
- **Citability**: +3 pts if average citability score ≥80; +1.5 pts if ≥60
- **AI Answer Readiness**: +2 pts if ≥50% of pages have entity signals

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
from packages.geo_audit.scorer import compute_score

score = compute_score(
    issues=geo_issues,
    pages_crawled=crawl_summary.pages_crawled,
    pages_with_entity_signals=entity_pages_count,
    pages_with_proof_signals=proof_pages_count,
    llms_txt_found=llms_txt_present,
    homepage_has_org_schema=homepage_has_org,
    avg_citability_score=avg_citability,
)
```

---

*Last updated:* 2025-05-07
*Branch:* `feature/backend-phase2`