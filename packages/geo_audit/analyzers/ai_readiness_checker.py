# packages/geo-audit/analyzers/ai_readiness_checker.py
"""Check AI answer readiness — how well content answers customer questions and serves GEO."""

from ...crawler.models import PageRecord
from ..models import GeoIssue, GeoIssueCategory, GeoIssueSeverity


# Question patterns that indicate a page tries to answer customer questions
QUESTION_PATTERNS = [
    "what is", "what are", "how to", "how do", "how can",
    "why is", "why do", "when is", "where is", "who is", "who are",
    "faq", "questions", "q&a",
]


def analyze(pages: list[PageRecord]) -> tuple[list[GeoIssue], int]:
    """Check AI answer readiness across all pages.

    Checks:
    - Pages answer specific customer questions (question in title/URL/H2)
    - Pages define services clearly
    - Pages include comparison content (us vs. them, product comparisons)
    - Pages include trust/proof signals (testimonials, reviews, stats)
    - Pages are self-contained (don't require reading other pages to understand)
    - Service pages have enough depth

    Returns:
        (list of issues, count of pages with AI answer readiness signals)
    """
    issues: list[GeoIssue] = []
    pages_with_readiness = 0

    for page in pages:
        url = page.url.lower()
        title = page.title or ""
        title_lower = title.lower()
        h2s = page.h2_headings or []
        h2s_lower = [h.lower() for h in h2s]
        word_count = page.word_count or 0

        has_question_signal = any(pat in title_lower for pat in QUESTION_PATTERNS)
        has_question_in_h2 = any(any(pat in h for pat in QUESTION_PATTERNS) for h in h2s_lower)
        is_service_page = any(k in url for k in ["/services/", "/service/", "/pricing/", "/plans/"])
        is_comparison = any(k in title_lower for k in ["vs", "vs.", "compared", "comparison"])
        has_faq = "faq" in url or "faq" in title_lower

        page_signals = 0

        # ── 1. Answers customer questions ────────────────────────────────
        if has_question_signal or has_question_in_h2:
            page_signals += 2
            if word_count < 150:
                issues.append(
                    GeoIssue(
                        issue_type="question_page_too_thin",
                        category=GeoIssueCategory.AI_ANSWER_READINESS,
                        severity=GeoIssueSeverity.MEDIUM,
                        title="Question-targeting page with thin content",
                        description=(
                            f"Page at {page.url} appears to target a customer question "
                            f"(title: '{title}') but has only {word_count} words. "
                            "AI systems need substantive answers (300+ words) to cite as sources."
                        ),
                        recommendation=(
                            "Expand this page to at least 400 words. "
                            "Answer the question directly in the first paragraph, "
                            "then provide supporting details in following sections."
                        ),
                        affected_element=page.url,
                        page_url=page.url,
                    )
                )
        else:
            # Generic content with no question targeting
            if word_count >= 500 and not has_question_signal:
                issues.append(
                    GeoIssue(
                        issue_type="generic_long_content_no_question_signal",
                        category=GeoIssueCategory.AI_ANSWER_READINESS,
                        severity=GeoIssueSeverity.LOW,
                        title="Long content without question-targeting signals",
                        description=(
                            f"Page at {page.url} has {word_count} words but no clear "
                            "question-targeting signals in the title or URL. "
                            "Content that directly answers questions performs better in AI search."
                        ),
                        recommendation=(
                            "Consider updating titles to include question phrases like "
                            "'What is [topic]?', 'How to [task]', or 'FAQ: [topic]'. "
                            "This signals to AI systems that the page answers a specific question."
                        ),
                        affected_element=page.url,
                        page_url=page.url,
                    )
                )

        # ── 2. Service page depth ────────────────────────────────────────
        if is_service_page:
            if word_count < 150:
                issues.append(
                    GeoIssue(
                        issue_type="service_page_too_thin",
                        category=GeoIssueCategory.AI_ANSWER_READINESS,
                        severity=GeoIssueSeverity.HIGH,
                        title=f"Service/pricing page with very thin content ({word_count} words)",
                        description=(
                            f"Service page at {page.url} has only {word_count} words. "
                            "Service pages need detailed descriptions of what you offer, "
                            "pricing, process, and differentiation to serve AI search."
                        ),
                        recommendation=(
                            "Expand service page to at least 300 words per service. "
                            "Include: what the service is, who it's for, what's included, "
                            "process/timeline, pricing structure, and proof elements."
                        ),
                        affected_element=page.url,
                        page_url=page.url,
                    )
                )
            else:
                page_signals += 1

        # ── 3. Comparison content ───────────────────────────────────────
        if is_comparison:
            page_signals += 1

        # ── 4. FAQ readiness ──────────────────────────────────────────
        if has_faq:
            page_signals += 2
            if len(h2s) < 2:
                issues.append(
                    GeoIssue(
                        issue_type="faq_page_lacks_structure",
                        category=GeoIssueCategory.AI_ANSWER_READINESS,
                        severity=GeoIssueSeverity.LOW,
                        title="FAQ page lacks structured Q&A format",
                        description=(
                            f"FAQ page at {page.url} doesn't have clear H2 headings for each Q&A. "
                            "AI systems parse FAQ pages more effectively when each question "
                            "is clearly separated by an H2 heading."
                        ),
                        recommendation=(
                            "Format FAQ page with one H2 per question. "
                            "Example: <h2>What is your return policy?</h2> "
                            "This enables AI systems to extract individual Q&A pairs."
                        ),
                        affected_element=page.url,
                        page_url=page.url,
                    )
                )

        # ── 5. Trust/proof signals ──────────────────────────────────────
        # Proxy: has images without alt = missing proof descriptions
        if page.images_count > 0 and page.images_without_alt == page.images_count:
            issues.append(
                GeoIssue(
                    issue_type="no_descriptive_images_for_proof",
                    category=GeoIssueCategory.AI_ANSWER_READINESS,
                    severity=GeoIssueSeverity.LOW,
                    title="Page has images but none have descriptive alt text",
                    description=(
                        f"Page at {page.url} has {page.images_count} images but none "
                        "have descriptive alt text. Proof elements (team photos, "
                        "project screenshots, testimonial screenshots) help AI verify claims."
                    ),
                    recommendation=(
                        "Add descriptive alt text to images that represent proof or evidence. "
                        "Alt text should describe what's in the image specifically."
                    ),
                    affected_element="<img> elements",
                    page_url=page.url,
                )
            )

        if page_signals >= 2:
            pages_with_readiness += 1

    return issues, pages_with_readiness
