# packages/seo-audit/analyzers/link_analyzer.py
"""Analyze internal and external links for crawlability and anchor text quality."""

from ...crawler.models import PageRecord
from ...models import AuditIssue, IssueCategory, IssueSeverity


INTERNAL_LINKS_MIN = 2   # pages should have at least some internal links


def analyze(page: PageRecord) -> list[AuditIssue]:
    """Analyze links on a page.

    Checks:
    - Internal link count (very low = orphan page risk)
    - External link count (suspiciously many outbound links)
    - Ratio of internal to external links for navigation quality
    """
    issues: list[AuditIssue] = []
    internal = page.internal_links_count
    external = page.external_links_count
    word_count = page.word_count or 0

    # Orphan page check: very few internal links on content-rich pages
    if word_count >= 200 and internal < INTERNAL_LINKS_MIN:
        issues.append(
            AuditIssue(
                issue_type="low_internal_link_count",
                category=IssueCategory.ARCHITECTURE,
                severity=IssueSeverity.HIGH,
                title=f"Few internal links ({internal}) for content-rich page",
                description=(
                    f"This page has {internal} internal links and {word_count} words. "
                    "Pages with substantial content should have internal links to related pages "
                    "to distribute page authority (PageRank) and help search engines discover content. "
                    "This page may be orphaned from the site's link graph."
                ),
                recommendation=(
                    "Add 3-10 contextual internal links to related pages, category pages, "
                    "or blog posts where naturally relevant. Use descriptive anchor text "
                    "that includes relevant keywords."
                ),
                affected_element="<a href> (internal)",
                page_url=page.url,
            )
        )

    # No internal links at all (not even nav)
    if internal == 0 and word_count >= 100:
        issues.append(
            AuditIssue(
                issue_type="no_internal_links",
                category=IssueCategory.ARCHITECTURE,
                severity=IssueSeverity.CRITICAL,
                title="Page has no internal links",
                description=(
                    f"This page at {page.url} has zero internal links. "
                    "This means search engines cannot discover this page from other pages on the site, "
                    "and any page authority cannot flow to or from this page. "
                    "This page is effectively an orphan."
                ),
                recommendation=(
                    "Add navigation links and/or contextual in-content links to this page from "
                    "related pages, category pages, header/footer navigation, or XML sitemaps. "
                    "Ensure at least one crawlable path exists from the homepage to this page."
                ),
                affected_element="<a href> (internal)",
                page_url=page.url,
            )
        )

    return issues
