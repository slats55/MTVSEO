# packages/geo-audit/analyzers/citability_scorer.py
"""Score each page on citability for AI search — how well it can serve as a direct source.

Citability signals evaluated per page:
  - Direct answer clarity: does the page answer specific questions clearly?
  - Factual density: numbers, statistics, named entities, dates
  - Business specificity: specific to this business (not generic)
  - Source/proof: citations, references, testimonials with names
  - Author/entity clarity: author bio, author name, author page
  - Structured headings: uses H2/H3 to organize content into scannable sections
  - Self-contained paragraphs: each paragraph makes sense without reading surrounding context
  - FAQ readiness: structured FAQ section or clear Q&A format

Returns a per-page citability score (0-100) and per-page GeoIssues.
"""

from packages.crawler.models import PageRecord
from packages.geo_audit.models import GeoIssue, GeoIssueCategory, GeoIssueSeverity


# Minimum word counts for content to be considered substantive
MIN_CONTENT_WORDS = 100
MIN_PARAGRAPH_WORDS = 20


def score_page_citability(page: PageRecord) -> tuple[int, list[GeoIssue]]:
    """Score a single page on citability for AI search.

    Args:
        page: PageRecord from crawler

    Returns:
        (score_out_of_100, list_of_issues)
    """
    issues: list[GeoIssue] = []
    score = 100

    url = page.url
    title = page.title or ""
    meta_desc = page.meta_description or ""
    h1 = page.h1 or ""
    h2s = page.h2_headings or []
    word_count = page.word_count or 0

    # ── 1. Direct Answer Clarity (max -20) ──────────────────────────────
    # Indicator: has FAQ-style content, clear lists, structured steps
    has_faq = "faq" in url.lower() or "question" in url.lower()
    has_list_content = len(h2s) >= 2  # multiple sections suggest organized answers
    if word_count < MIN_CONTENT_WORDS:
        score -= 15
        issues.append(_make_issue(
            "thin_content_poor_citability",
            GeoIssueCategory.CITABILITY,
            GeoIssueSeverity.MEDIUM,
            f"Thin content ({word_count} words) reduces citability",
            f"Pages with only {word_count} words cannot provide substantive answers "
            f"to user questions. AI systems prefer citing pages with comprehensive coverage.",
            "Expand content to at least 300 words with specific answers to likely questions.",
            url,
        ))
    elif not has_faq and not has_list_content:
        score -= 5  # no structured answer signals

    # ── 2. Factual Density (max -15) ──────────────────────────────────
    # Proxy: word count + heading structure
    if word_count >= 500 and len(h2s) >= 3:
        pass  # Good — substantial and organized
    elif word_count >= 300 and len(h2s) >= 2:
        score -= 5  # OK but could be better
    elif word_count < 200:
        score -= 10
        issues.append(_make_issue(
            "low_factual_density",
            GeoIssueCategory.CITABILITY,
            GeoIssueSeverity.LOW,
            "Low factual density — sparse content",
            "This page has limited content depth. AI citability benefits from pages "
            "with named entities, statistics, dates, and specific details.",
            "Add specific facts, numbers, dates, and named entities to increase "
            "factual density and demonstrate expertise.",
            url,
        ))

    # ── 3. Business Specificity (max -15) ─────────────────────────────
    # Check if title/meta suggest generic content vs. business-specific
    generic_keywords = ["how to", "what is", "guide", "tutorial", "best", "top"]
    title_lower = title.lower()
    is_generic = any(k in title_lower for k in generic_keywords)
    if is_generic and word_count < 300:
        score -= 10
        issues.append(_make_issue(
            "generic_content_not_business_specific",
            GeoIssueCategory.CITABILITY,
            GeoIssueSeverity.LOW,
            "Generic content — not business-specific",
            "This page uses generic keywords (how to, best, guide) without specific "
            "business differentiation. AI systems prefer citing sources with unique "
            "business-specific expertise and proof.",
            "Add business-specific details: your specific process, your results, "
            "your team's specific approach, your unique methodology.",
            url,
        ))

    # ── 4. Source/Proof Signals (max -20) ─────────────────────────────
    # Proxy: images_with_alt and word_count suggest proof
    if page.images_count > 0 and page.images_without_alt == 0:
        pass  # Good — all images have alt (likely described)
    elif page.images_without_alt > 0:
        score -= 5
        issues.append(_make_issue(
            "images_missing_descriptions",
            GeoIssueCategory.CITABILITY,
            GeoIssueSeverity.LOW,
            "Images missing descriptive alt text",
            "Images without alt text cannot serve as proof or context for AI citations. "
            "Descriptive alt text helps AI systems understand visual proof elements.",
            "Add descriptive alt text to all images that represent proof or evidence.",
            url,
        ))

    # ── 5. Author/Entity Clarity (max -15) ─────────────────────────────
    # We can't easily detect author names from raw HTML without NLP,
    # but we can flag if the page has author signals (byline text patterns)
    # This is a placeholder — full implementation would need NLP
    if "author" in meta_desc.lower() or "by " in (h1.lower() + title.lower()):
        pass  # Has some author signal
    elif word_count >= 500:
        score -= 5  # Long content without obvious author signal

    # ── 6. Structured Headings (max -15) ──────────────────────────────
    if len(h2s) == 0 and word_count >= 200:
        score -= 10
        issues.append(_make_issue(
            "no_heading_structure",
            GeoIssueCategory.CITABILITY,
            GeoIssueSeverity.MEDIUM,
            "No H2 headings — poor content structure",
            "Long-form content without H2 headings is hard for AI systems to parse "
            "and understand as organized answers. Section headings help AI identify "
            "specific answers within a page.",
            "Add H2 headings to divide content into distinct topics or questions. "
            "Each H2 should introduce a specific sub-topic.",
            url,
        ))
    elif len(h2s) == 0 and word_count < 200:
        score -= 5

    # ── 7. Self-contained paragraphs ───────────────────────────────────
    # Proxy: short pages with no headings = potentially thin/fragmented
    if word_count < 100 and len(h2s) == 0:
        score -= 10
        issues.append(_make_issue(
            "fragmented_content",
            GeoIssueCategory.CITABILITY,
            GeoIssueSeverity.MEDIUM,
            "Fragmented content — lacks substantive paragraphs",
            "This page appears to have very little readable content. "
            "AI citability requires self-contained paragraphs that answer questions.",
            "Add at least 2-3 paragraphs of 100+ words each.",
            url,
        ))

    # ── 8. FAQ Readiness (max -10) ────────────────────────────────────
    has_faq_heading = any("faq" in h.lower() for h in h2s)
    if has_faq_heading:
        pass  # Good
    elif has_faq and len(h2s) >= 3:
        pass  # URL has faq and has structure
    elif "faq" in title_lower or "question" in title_lower:
        score -= 5  # FAQ topic but no FAQ heading

    score = max(0, score)
    return score, issues


def _make_issue(
    issue_type: str,
    category: GeoIssueCategory,
    severity: GeoIssueSeverity,
    title: str,
    description: str,
    recommendation: str,
    page_url: str,
) -> GeoIssue:
    return GeoIssue(
        issue_type=issue_type,
        category=category,
        severity=severity,
        title=title,
        description=description,
        recommendation=recommendation,
        affected_element=None,
        page_url=page_url,
    )
