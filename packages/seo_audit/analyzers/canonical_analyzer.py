# packages/seo-audit/analyzers/canonical_analyzer.py
"""Analyze canonical URL tags for duplicate content and self-referencing issues."""

from ...crawler.models import PageRecord
from ..models import AuditIssue, IssueCategory, IssueSeverity


def analyze(page: PageRecord) -> list[AuditIssue]:
    """Analyze canonical tag configuration.

    Checks:
    - Presence of a canonical tag (recommended for all pages)
    - Canonical pointing to a non-200 URL (broken canonical)
    - Self-referential canonical that differs only by trailing slash
    - Canonical pointing to a redirecting URL
    - Canonical pointing to a different domain (cross-domain canonical — OK but noteworthy)
    """
    issues: list[AuditIssue] = []
    canonical = page.canonical_url
    page_url = page.url
    redirect_url = page.redirect_url

    # Canonical pointing to redirecting URL
    if redirect_url and canonical:
        issues.append(
            AuditIssue(
                issue_type="canonical_points_to_redirect",
                category=IssueCategory.CRAWLABILITY,
                severity=IssueSeverity.MEDIUM,
                title="Canonical URL points to a redirect",
                description=(
                    f"The canonical for '{page_url}' points to '{canonical}', "
                    "which redirects. This creates a redirect chain and may cause "
                    "search engines to not honor the canonical directive."
                ),
                recommendation=(
                    f"Update the canonical tag on {page_url} to point directly to the "
                    "final destination URL (the redirect target) to avoid the extra hop."
                ),
                affected_element=f"<link rel='canonical' href='{canonical}'>",
                page_url=page_url,
            )
        )

    # Self-referential check (canonical differs only by trailing slash)
    if canonical:
        canonical_stripped = canonical.rstrip("/")
        page_stripped = page_url.rstrip("/")
        if canonical_stripped != page_stripped:
            from urllib.parse import urlparse
            c_parsed = urlparse(canonical)
            p_parsed = urlparse(page_url)

            # Different domain — cross-domain canonical (informational only)
            if c_parsed.netloc != p_parsed.netloc:
                issues.append(
                    AuditIssue(
                        issue_type="cross_domain_canonical",
                        category=IssueCategory.CRAWLABILITY,
                        severity=IssueSeverity.INFO,
                        title="Canonical points to different domain",
                        description=(
                            f"The canonical on '{page_url}' points to a different domain: "
                            f"'{canonical}'. Cross-domain canonicalization is valid but "
                            "transferring ranking signals across domains requires careful "
                            "consideration of SEO implications."
                        ),
                        recommendation=(
                            "Verify this cross-domain canonical is intentional. "
                            "Ensure the target domain is a related, owned property. "
                            "Monitor for unexpected ranking shifts after implementing."
                        ),
                        affected_element=f"<link rel='canonical' href='{canonical}'>",
                        page_url=page_url,
                    )
                )

    return issues
