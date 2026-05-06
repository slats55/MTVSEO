# packages/seo-audit/analyzers/meta_analyzer.py
"""Analyze meta description tags for SEO quality issues."""

from ...crawler.models import PageRecord
from ...models import AuditIssue, IssueCategory, IssueSeverity


META_DESC_MIN_LEN = 120
META_DESC_MAX_LEN = 160


def analyze(page: PageRecord, all_descriptions: dict[str, int]) -> list[AuditIssue]:
    """Analyze a page's meta description tag.

    Checks:
    - Presence of a meta description
    - Length within optimal range (120-160 chars)
    - Uniqueness across the site (duplicate detection)
    - Keyword presence (bonus — informational only)
    """
    issues: list[AuditIssue] = []
    meta_desc = page.meta_description

    if not meta_desc or not meta_desc.strip():
        issues.append(
            AuditIssue(
                issue_type="missing_meta_description",
                category=IssueCategory.METADATA,
                severity=IssueSeverity.MEDIUM,
                title="Missing meta description",
                description=(
                    "This page has no meta description. While not a direct ranking factor, "
                    "meta descriptions are critical for click-through rates in search results. "
                    "Search engines may auto-generate a snippet from page content, "
                    "which is less controlled."
                ),
                recommendation=(
                    "Add a descriptive <meta name='description'> tag in the <head>. "
                    "Include a clear value proposition and a call to action within "
                    f"{META_DESC_MIN_LEN}-{META_DESC_MAX_LEN} characters."
                ),
                affected_element="<meta name='description'>",
                page_url=page.url,
            )
        )
        return issues  # No further checks possible without a description

    desc_text = meta_desc.strip()
    desc_len = len(desc_text)

    # Length check
    if desc_len < META_DESC_MIN_LEN:
        issues.append(
            AuditIssue(
                issue_type="meta_description_too_short",
                category=IssueCategory.METADATA,
                severity=IssueSeverity.LOW,
                title=f"Meta description too short ({desc_len} chars)",
                description=(
                    f"The meta description is {desc_len} characters. "
                    f"Optimal length is {META_DESC_MIN_LEN}-{META_DESC_MAX_LEN} characters. "
                    "Short descriptions may be auto-completed by search engines."
                ),
                recommendation=(
                    f"Expand the meta description to at least {META_DESC_MIN_LEN} characters "
                    "to fully control the search snippet."
                ),
                affected_element=f"<meta name='description' content='{desc_text}'>",
                page_url=page.url,
            )
        )
    elif desc_len > META_DESC_MAX_LEN:
        issues.append(
            AuditIssue(
                issue_type="meta_description_too_long",
                category=IssueCategory.METADATA,
                severity=IssueSeverity.LOW,
                title=f"Meta description too long ({desc_len} chars)",
                description=(
                    f"The meta description is {desc_len} characters. "
                    f"Search engines truncate descriptions beyond {META_DESC_MAX_LEN} characters."
                ),
                recommendation=(
                    f"Shorten the meta description to {META_DESC_MAX_LEN} characters or fewer. "
                    "Prioritize the most compelling information."
                ),
                affected_element=f"<meta name='description' content='{desc_text[:META_DESC_MAX_LEN]}...'>",
                page_url=page.url,
            )
        )

    # Duplicate description check
    count = all_descriptions.get(desc_text.lower().strip(), 0)
    if count > 1:
        issues.append(
            AuditIssue(
                issue_type="duplicate_meta_description",
                category=IssueCategory.METADATA,
                severity=IssueSeverity.MEDIUM,
                title=f"Duplicate meta description ({count} pages)",
                description=(
                    f"The meta description '{desc_text[:60]}...' is shared by {count} pages. "
                    "Duplicate meta descriptions reduce the diversity of search snippets "
                    "and may harm CTR for multiple pages simultaneously."
                ),
                recommendation=(
                    "Write a unique meta description for each page that accurately "
                    "summarizes that page's specific content."
                ),
                affected_element=f"<meta name='description' content='{desc_text}'>",
                page_url=page.url,
                count=count,
            )
        )

    return issues
