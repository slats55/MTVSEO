# packages/geo-audit/scorer.py
"""Compute the 0-100 GEO / AI visibility score from issues and page metrics."""

from .models import GeoIssue, GeoIssueCategory, GeoIssueSeverity, GeoScore


# Weights (sum = 100)
CATEGORY_WEIGHTS = {
    GeoIssueCategory.AI_CRAWLER_ACCESS:      15,
    GeoIssueCategory.ENTITY_OPTIMIZATION:    15,
    GeoIssueCategory.CITABILITY:             25,
    GeoIssueCategory.AI_ANSWER_READINESS:    20,
    GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION: 10,
    GeoIssueCategory.SCHEMA:                 10,  # merged into entity/score
    GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION: 5,
}

MAX_PER_CATEGORY = dict(CATEGORY_WEIGHTS)

SEVERITY_PENALTIES = {
    GeoIssueSeverity.CRITICAL: {
        GeoIssueCategory.AI_CRAWLER_ACCESS:     6,
        GeoIssueCategory.ENTITY_OPTIMIZATION:   6,
        GeoIssueCategory.CITABILITY:            10,
        GeoIssueCategory.AI_ANSWER_READINESS:    8,
        GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION: 3,
        GeoIssueCategory.SCHEMA:                 4,
    },
    GeoIssueSeverity.HIGH: {
        GeoIssueCategory.AI_CRAWLER_ACCESS:     4,
        GeoIssueCategory.ENTITY_OPTIMIZATION:   4,
        GeoIssueCategory.CITABILITY:             6,
        GeoIssueCategory.AI_ANSWER_READINESS:    5,
        GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION: 2,
        GeoIssueCategory.SCHEMA:                 3,
    },
    GeoIssueSeverity.MEDIUM: {
        GeoIssueCategory.AI_CRAWLER_ACCESS:     2,
        GeoIssueCategory.ENTITY_OPTIMIZATION:   2,
        GeoIssueCategory.CITABILITY:            4,
        GeoIssueCategory.AI_ANSWER_READINESS:   3,
        GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION: 1,
        GeoIssueCategory.SCHEMA:                 1.5,
    },
    GeoIssueSeverity.LOW: {
        GeoIssueCategory.AI_CRAWLER_ACCESS:     1,
        GeoIssueCategory.ENTITY_OPTIMIZATION:   1,
        GeoIssueCategory.CITABILITY:            2,
        GeoIssueCategory.AI_ANSWER_READINESS:   1,
        GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION: 0.5,
        GeoIssueCategory.SCHEMA:                 0.5,
    },
    GeoIssueSeverity.INFO: {},
}


def compute_score(
    issues: list[GeoIssue],
    pages_crawled: int,
    pages_with_entity_signals: int,
    pages_with_proof_signals: int,
    llms_txt_found: bool,
    homepage_has_org_schema: bool,
    avg_citability_score: float,
) -> GeoScore:
    """Compute GeoScore from issues and aggregate metrics.

    Args:
        issues:              all GeoIssues found
        pages_crawled:       total pages successfully crawled
        pages_with_entity_signals: pages with Organization/schema signals
        pages_with_proof_signals: pages with proof elements (images + alt, testimonials)
        llms_txt_found:      whether llms.txt exists
        homepage_has_org_schema: homepage has Organization schema
        avg_citability_score: average citability score (0-100) across pages

    Returns:
        GeoScore with per-category and total scores
    """
    scores: dict[GeoIssueCategory, float] = {
        cat: float(max_pts) for cat, max_pts in MAX_PER_CATEGORY.items()
    }
    penalties: dict[GeoIssueCategory, float] = {cat: 0.0 for cat in GeoIssueCategory}

    for issue in issues:
        severity = issue.severity
        category = issue.category
        count = max(issue.count, 1)
        base_penalty = SEVERITY_PENALTIES.get(severity, {}).get(category, 0.0)
        scale = min(count / pages_crawled * 10, 3.0) if pages_crawled > 0 else 1.0
        penalty = base_penalty * scale
        penalties[category] = min(penalties[category] + penalty, MAX_PER_CATEGORY[category])

    for cat in GeoIssueCategory:
        scores[cat] = max(0.0, scores[cat] - penalties[cat])

    # ── Bonuses ────────────────────────────────────────────────────────────
    # Entity clarity bonus
    if homepage_has_org_schema:
        scores[GeoIssueCategory.ENTITY_OPTIMIZATION] = min(
            scores[GeoIssueCategory.ENTITY_OPTIMIZATION] + 3,
            MAX_PER_CATEGORY[GeoIssueCategory.ENTITY_OPTIMIZATION]
        )

    # LLM output optimization bonus
    if llms_txt_found:
        scores[GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION] = min(
            scores[GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION] + 2,
            MAX_PER_CATEGORY[GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION]
        )

    # Citability bonus based on average score
    if avg_citability_score >= 80:
        scores[GeoIssueCategory.CITABILITY] = min(
            scores[GeoIssueCategory.CITABILITY] + 3,
            MAX_PER_CATEGORY[GeoIssueCategory.CITABILITY]
        )
    elif avg_citability_score >= 60:
        scores[GeoIssueCategory.CITABILITY] = min(
            scores[GeoIssueCategory.CITABILITY] + 1.5,
            MAX_PER_CATEGORY[GeoIssueCategory.CITABILITY]
        )

    # AI answer readiness bonus
    if pages_crawled > 0:
        readiness_pct = pages_with_entity_signals / pages_crawled
        if readiness_pct >= 0.5:
            scores[GeoIssueCategory.AI_ANSWER_READINESS] = min(
                scores[GeoIssueCategory.AI_ANSWER_READINESS] + 2,
                MAX_PER_CATEGORY[GeoIssueCategory.AI_ANSWER_READINESS]
            )

    for cat in GeoIssueCategory:
        scores[cat] = min(scores[cat], float(MAX_PER_CATEGORY[cat]))

    return GeoScore(
        ai_crawler_access=round(scores[GeoIssueCategory.AI_CRAWLER_ACCESS], 2),
        entity_clarity=round(scores[GeoIssueCategory.ENTITY_OPTIMIZATION], 2),
        citability=round(scores[GeoIssueCategory.CITABILITY], 2),
        content_depth=round(scores[GeoIssueCategory.AI_ANSWER_READINESS], 2),
        schema=round(scores[GeoIssueCategory.SCHEMA], 2),
        brand_authority=round(scores.get(GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION, 5.0), 2),
        llm_readability=round(scores[GeoIssueCategory.LLM_OUTPUT_OPTIMIZATION], 2),
    )
