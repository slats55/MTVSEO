# packages/seo-audit/analyzers/heading_analyzer.py
"""Analyze heading structure (H1, H2, H3 hierarchy) for SEO quality."""

from ...crawler.models import PageRecord
from ..models import AuditIssue, IssueCategory, IssueSeverity


def analyze(page: PageRecord, h1_count: int, h2_counts: dict[str, int]) -> list[AuditIssue]:
    """Analyze heading tag hierarchy.

    Checks:
    - Exactly one H1 per page (best practice)
    - Presence of an H1 tag
    - Multiple H1 tags (should be one per page)
    - Missing H2 tags on pages with long content
    - Heading hierarchy (H1 → H2 → H3, no skipping levels)
    - Orphan H2s (H2 without preceding H1 context)
    """
    issues: list[AuditIssue] = []
    h1 = page.h1
    h2s = page.h2_headings or []

    # H1 presence and count
    if h1_count == 0:
        issues.append(
            AuditIssue(
                issue_type="missing_h1",
                category=IssueCategory.METADATA,
                severity=IssueSeverity.HIGH,
                title="Missing H1 heading",
                description=(
                    "This page has no H1 tag. The H1 should contain the primary heading "
                    "that tells both users and search engines what the main topic of the page is. "
                    f"Page: {page.url}"
                ),
                recommendation=(
                    "Add a single <h1> tag that clearly describes the page's main topic. "
                    "Include the primary keyword near the start of the H1."
                ),
                affected_element="<h1>",
                page_url=page.url,
            )
        )
    elif h1_count > 1:
        issues.append(
            AuditIssue(
                issue_type="multiple_h1",
                category=IssueCategory.METADATA,
                severity=IssueSeverity.HIGH,
                title=f"Multiple H1 tags ({h1_count} found)",
                description=(
                    f"This page has {h1_count} H1 tags. Best practice is exactly one H1 "
                    "per page to clearly establish the main topic. Multiple H1s dilute "
                    "the signal and confuse search engines about the primary subject."
                ),
                recommendation=(
                    "Use only one <h1> per page. Move secondary headings to <h2>, <h3>, etc. "
                    "If multiple H1s are structurally necessary, consider whether the content "
                    "should be split into separate pages."
                ),
                affected_element=f"<h1> (x{h1_count})",
                page_url=page.url,
                count=h1_count,
            )
        )

    # H1 content checks
    if h1:
        h1_text = h1.strip()
        if len(h1_text) > 70:
            issues.append(
                AuditIssue(
                    issue_type="h1_too_long",
                    category=IssueCategory.METADATA,
                    severity=IssueSeverity.LOW,
                    title=f"H1 heading too long ({len(h1_text)} chars)",
                    description=(
                        f"The H1 '{h1_text}' is {len(h1_text)} characters. "
                        "Long headings may be truncated in search results and "
                        "typically indicate keyword stuffing or lack of focus."
                    ),
                    recommendation=(
                        "Keep H1 headings under 70 characters. "
                        "Be concise and front-load the primary keyword."
                    ),
                    affected_element=f"<h1>{h1_text[:70]}...</h1>",
                    page_url=page.url,
                )
            )

    # H2 presence on pages with significant content
    word_count = page.word_count or 0
    if word_count >= 300 and len(h2s) == 0:
        issues.append(
            AuditIssue(
                issue_type="missing_h2_headings",
                category=IssueCategory.ARCHITECTURE,
                severity=IssueSeverity.MEDIUM,
                title="No H2 headings on long-form content page",
                description=(
                    f"This page has {word_count} words but no H2 headings. "
                    "Long-form content without section headings is difficult for users to scan "
                    "and provides no semantic structure for search engines to understand "
                    "the page's organization."
                ),
                recommendation=(
                    "Add H2 headings to divide the content into logical sections. "
                    "Each H2 should introduce a sub-topic related to the H1 topic. "
                    "Use 2-5 H2s depending on content length."
                ),
                affected_element="<h2>",
                page_url=page.url,
            )
        )

    return issues
