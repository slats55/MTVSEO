# packages/seo-audit/analyzers/title_analyzer.py
"""Analyze page titles for SEO quality issues."""

from ...crawler.models import PageRecord
from ..models import AuditIssue, IssueCategory, IssueSeverity


TITLE_MIN_LEN = 30
TITLE_MAX_LEN = 60


def analyze(page: PageRecord, all_titles: dict[str, int]) -> list[AuditIssue]:
    """Analyze a page's title tag.

    Checks:
    - Presence of a title tag
    - Length within optimal range (30-60 chars)
    - Uniqueness across the site (duplicate detection)
    - Brand suffix pattern (+ | or - separators)
    """
    issues: list[AuditIssue] = []
    title = page.title

    if not title or not title.strip():
        issues.append(
            AuditIssue(
                issue_type="missing_title",
                category=IssueCategory.METADATA,
                severity=IssueSeverity.HIGH,
                title="Missing title tag",
                description=(
                    "This page has no <title> tag. Search engines rely on the title tag "
                    "to understand page content and generate snippets in search results. "
                    f"Page: {page.url}"
                ),
                recommendation=(
                    "Add a descriptive <title> tag within the <head> section. "
                    "Include the primary keyword near the beginning and the brand name "
                    "as a suffix if used site-wide."
                ),
                affected_element="<title>",
                page_url=page.url,
            )
        )
        return issues  # No point running further checks without a title

    title_text = title.strip()
    title_len = len(title_text)

    # Length check
    if title_len < TITLE_MIN_LEN:
        issues.append(
            AuditIssue(
                issue_type="title_too_short",
                category=IssueCategory.METADATA,
                severity=IssueSeverity.MEDIUM,
                title=f"Title too short ({title_len} chars)",
                description=(
                    f"The title '{title_text}' is {title_len} characters long. "
                    f"Optimal titles are {TITLE_MIN_LEN}-{TITLE_MAX_LEN} characters. "
                    "Short titles may not convey enough context to searchers or engines."
                ),
                recommendation=(
                    f"Expand the title to at least {TITLE_MIN_LEN} characters. "
                    "Include the primary keyword and a unique selling point or descriptor."
                ),
                affected_element=f"<title>{title_text}</title>",
                page_url=page.url,
            )
        )
    elif title_len > TITLE_MAX_LEN:
        issues.append(
            AuditIssue(
                issue_type="title_too_long",
                category=IssueCategory.METADATA,
                severity=IssueSeverity.MEDIUM,
                title=f"Title too long ({title_len} chars)",
                description=(
                    f"The title '{title_text}' is {title_len} characters long. "
                    f"Search engines typically display only {TITLE_MAX_LEN} characters. "
                    "Text beyond this limit gets truncated with '...' in search results."
                ),
                recommendation=(
                    f"Shorten the title to {TITLE_MAX_LEN} characters or fewer. "
                    "Put the most important keywords first."
                ),
                affected_element=f"<title>{title_text[:TITLE_MAX_LEN]}...</title>",
                page_url=page.url,
            )
        )

    # Duplicate title check
    count = all_titles.get(title_text.lower().strip(), 0)
    if count > 1:
        issues.append(
            AuditIssue(
                issue_type="duplicate_title",
                category=IssueCategory.METADATA,
                severity=IssueSeverity.MEDIUM,
                title=f"Duplicate title ({count} pages)",
                description=(
                    f"The title '{title_text}' is used on {count} pages. "
                    "Duplicate titles make it difficult for search engines to distinguish "
                    "between pages, diluting ranking signals."
                ),
                recommendation=(
                    "Rewrite the title for this page to be unique. "
                    "Include the page's specific topic, product, service, or location "
                    "to differentiate it from the other pages sharing this title."
                ),
                affected_element=f"<title>{title_text}</title>",
                page_url=page.url,
                count=count,
            )
        )

    return issues
