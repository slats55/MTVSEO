# packages/seo-audit/scorer.py
"""Compute the 0-100 SEO audit score from a list of issues and page metrics.

Scoring model (sum = 100):
  Crawlability:       20 pts
  Indexability:        20 pts
  Metadata:            15 pts
  Architecture:        15 pts
  Performance:         15 pts  (placeholder — actual PageSpeed data comes from integrations)
  Structured Data:     10 pts
  Security:            5 pts
"""

from .models import AuditIssue, AuditScore, IssueCategory, IssueSeverity


# ─── Weights (must sum to 100) ────────────────────────────────────────────────

CATEGORY_WEIGHTS = {
    IssueCategory.CRAWLABILITY:      20,
    IssueCategory.INDEXABILITY:     20,
    IssueCategory.METADATA:         15,
    IssueCategory.ARCHITECTURE:      15,
    IssueCategory.PERFORMANCE:       15,
    IssueCategory.STRUCTURED_DATA:   10,
    IssueCategory.SECURITY:          5,
}

# Max points available per category (same as weights)
MAX_PER_CATEGORY = dict(CATEGORY_WEIGHTS)

# Penalty per issue severity per category
# Format: {severity: {category: max_penalty}}
# The actual penalty is scaled by the count of affected pages
SEVERITY_PENALTIES = {
    IssueSeverity.CRITICAL: {
        IssueCategory.CRAWLABILITY:    8,
        IssueCategory.INDEXABILITY:   8,
        IssueCategory.METADATA:        6,
        IssueCategory.ARCHITECTURE:     6,
        IssueCategory.PERFORMANCE:     6,
        IssueCategory.STRUCTURED_DATA: 4,
        IssueCategory.SECURITY:        3,
    },
    IssueSeverity.HIGH: {
        IssueCategory.CRAWLABILITY:    5,
        IssueCategory.INDEXABILITY:   5,
        IssueCategory.METADATA:        4,
        IssueCategory.ARCHITECTURE:    4,
        IssueCategory.PERFORMANCE:     4,
        IssueCategory.STRUCTURED_DATA: 3,
        IssueCategory.SECURITY:        2,
    },
    IssueSeverity.MEDIUM: {
        IssueCategory.CRAWLABILITY:    3,
        IssueCategory.INDEXABILITY:    3,
        IssueCategory.METADATA:         2,
        IssueCategory.ARCHITECTURE:     2,
        IssueCategory.PERFORMANCE:      2,
        IssueCategory.STRUCTURED_DATA:  1,
        IssueCategory.SECURITY:         1,
    },
    IssueSeverity.LOW: {
        IssueCategory.CRAWLABILITY:    1,
        IssueCategory.INDEXABILITY:    1,
        IssueCategory.METADATA:         1,
        IssueCategory.ARCHITECTURE:    1,
        IssueCategory.PERFORMANCE:     1,
        IssueCategory.STRUCTURED_DATA:  0.5,
        IssueCategory.SECURITY:        0.5,
    },
    IssueSeverity.INFO: {},  # No penalty
}

# Bonus points for good practices (additive within category)
BONUSES: dict[IssueCategory, float] = {
    IssueCategory.CRAWLABILITY:     0,   # handled via deductions
    IssueCategory.INDEXABILITY:    0,
    IssueCategory.METADATA:         0,
    IssueCategory.ARCHITECTURE:     0,
    IssueCategory.PERFORMANCE:      0,
    IssueCategory.STRUCTURED_DATA:  0,
    IssueCategory.SECURITY:         0,
}


def compute_score(
    issues: list[AuditIssue],
    pages_discovered: int,
    pages_crawled: int,
    pages_with_schema: int,
    pages_indexable: int,
    pages_4xx: int,
    pages_5xx: int,
    homepage_has_schema: bool = False,
) -> AuditScore:
    """Compute AuditScore from issues and aggregate page metrics.

    Args:
        issues:             all AuditIssues found across all pages
        pages_discovered:   total URLs discovered
        pages_crawled:      total URLs successfully fetched (status code received)
        pages_with_schema:  pages with at least one JSON-LD block
        pages_indexable:    pages without noindex directive
        pages_4xx:          pages returning HTTP 4xx
        pages_5xx:          pages returning HTTP 5xx
        homepage_has_schema: whether the homepage has Organization/WebSite schema

    Returns:
        AuditScore with per-category and total scores
    """
    # Start with full marks per category
    scores: dict[IssueCategory, float] = {
        cat: float(max_pts) for cat, max_pts in MAX_PER_CATEGORY.items()
    }

    # Aggregate penalties per category
    penalties: dict[IssueCategory, float] = {cat: 0.0 for cat in IssueCategory}

    for issue in issues:
        severity = issue.severity
        category = issue.category
        count = max(issue.count, 1)  # at least 1 page affected
        base_penalty = SEVERITY_PENALTIES.get(severity, {}).get(category, 0.0)
        # Scale penalty by page count (capped at 3x for site-wide issues)
        scale = min(count / pages_crawled * 10, 3.0) if pages_crawled > 0 else 1.0
        penalty = base_penalty * scale
        penalties[category] = min(penalties[category] + penalty, MAX_PER_CATEGORY[category])

    # Apply penalties
    for cat in IssueCategory:
        scores[cat] = max(0.0, scores[cat] - penalties[cat])

    # Apply bonuses for good practices
    # Structured data bonus
    if pages_crawled > 0:
        schema_pct = pages_with_schema / pages_crawled
        if schema_pct >= 0.8:
            scores[IssueCategory.STRUCTURED_DATA] += 2.0
        elif schema_pct >= 0.5:
            scores[IssueCategory.STRUCTURED_DATA] += 1.0

    # Indexability bonus (high ratio of indexable pages)
    if pages_crawled > 0:
        indexable_pct = pages_indexable / pages_crawled
        if indexable_pct >= 0.9:
            scores[IssueCategory.INDEXABILITY] += 2.0
        elif indexable_pct >= 0.75:
            scores[IssueCategory.INDEXABILITY] += 1.0

    # Crawlability bonus (low error rates)
    if pages_crawled > 0:
        error_pct = (pages_4xx + pages_5xx) / pages_crawled
        if error_pct <= 0.01:
            scores[IssueCategory.CRAWLABILITY] += 2.0
        elif error_pct <= 0.05:
            scores[IssueCategory.CRAWLABILITY] += 1.0

    # Cap all scores at their max
    for cat in IssueCategory:
        scores[cat] = min(scores[cat], float(MAX_PER_CATEGORY[cat]))

    return AuditScore(
        crawlability=round(scores[IssueCategory.CRAWLABILITY], 2),
        indexability=round(scores[IssueCategory.INDEXABILITY], 2),
        metadata=round(scores[IssueCategory.METADATA], 2),
        architecture=round(scores[IssueCategory.ARCHITECTURE], 2),
        performance=round(scores[IssueCategory.PERFORMANCE], 2),
        structured_data=round(scores[IssueCategory.STRUCTURED_DATA], 2),
        security=round(scores[IssueCategory.SECURITY], 2),
    )
