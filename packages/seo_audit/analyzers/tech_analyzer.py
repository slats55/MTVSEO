# packages/seo-audit/analyzers/tech_analyzer.py
"""Analyze technical SEO issues: HTTP status codes, redirects, robots meta, indexability."""

from ...crawler.models import PageRecord
from ...models import AuditIssue, IssueCategory, IssueSeverity


def analyze(page: PageRecord) -> list[AuditIssue]:
    """Analyze technical SEO issues on a page.

    Checks:
    - HTTP 4xx status codes (client errors)
    - HTTP 5xx status codes (server errors)
    - 3xx redirects and their chains
    - Meta robots noindex
    - HTTP/HTTPS mixed content signals
    - Thin content pages
    """
    issues: list[AuditIssue] = []
    status = page.status_code
    url = page.url
    is_indexable = page.is_indexable
    redirect_url = page.redirect_url

    # No response at all
    if status is None:
        issues.append(
            AuditIssue(
                issue_type="fetch_error",
                category=IssueCategory.CRAWLABILITY,
                severity=IssueSeverity.CRITICAL,
                title="Page failed to load",
                description=(
                    f"The page at {url} returned no HTTP response. "
                    "This could be a DNS failure, connection timeout, or server being down. "
                    "Search engines cannot index this page."
                ),
                recommendation=(
                    "Check if the server is running and accessible. "
                    "Verify DNS records are correct. "
                    "Check server logs for connection errors."
                ),
                affected_element=url,
                page_url=url,
            )
        )
        return issues  # No further checks possible

    # 4xx client errors
    if status == 404:
        issues.append(
            AuditIssue(
                issue_type="http_404",
                category=IssueCategory.CRAWLABILITY,
                severity=IssueSeverity.HIGH,
                title="Page not found (404)",
                description=(
                    f"The page at {url} returned HTTP 404 (Not Found). "
                    "This means the URL does not exist on the server. "
                    "If linked from other pages, this creates a poor user experience and "
                    "wastes crawl budget."
                ),
                recommendation=(
                    "Set up a custom 404 page that helps users find what they're looking for "
                    "and includes links to the homepage and popular pages. "
                    "Consider implementing 'soft 404' handling if this URL previously existed "
                    "and had links pointing to it."
                ),
                affected_element=url,
                page_url=url,
            )
        )
    elif status == 410:
        issues.append(
            AuditIssue(
                issue_type="http_410",
                category=IssueCategory.CRAWLABILITY,
                severity=IssueSeverity.HIGH,
                title="Page permanently removed (410)",
                description=(
                    f"The page at {url} returned HTTP 410 (Gone). "
                    "This signals that the content has been intentionally removed. "
                    "Ensure there are no valuable links pointing to this URL."
                ),
                recommendation=(
                    "Verify this URL should remain gone. "
                    "Redirect to a relevant page if there are links pointing here. "
                    "Update or remove any internal links pointing to this URL."
                ),
                affected_element=url,
                page_url=url,
            )
        )
    elif status >= 400 and status < 500:
        issues.append(
            AuditIssue(
                issue_type="http_4xx",
                category=IssueCategory.CRAWLABILITY,
                severity=IssueSeverity.HIGH,
                title=f"HTTP {status} client error",
                description=(
                    f"The page at {url} returned HTTP {status}. "
                    "This indicates a client error preventing access to the page."
                ),
                recommendation=(
                    f"Fix the server-side issue causing HTTP {status}. "
                    "Common causes: incorrect URL, missing permissions (403), "
                    "or content requiring authentication (401)."
                ),
                affected_element=url,
                page_url=url,
            )
        )

    # 5xx server errors
    if status >= 500:
        issues.append(
            AuditIssue(
                issue_type="http_5xx",
                category=IssueCategory.CRAWLABILITY,
                severity=IssueSeverity.CRITICAL,
                title=f"HTTP {status} server error",
                description=(
                    f"The page at {url} returned HTTP {status}. "
                    "Server errors indicate the server encountered an unexpected condition. "
                    "These are directly harmful to SEO as search engines cannot index the content."
                ),
                recommendation=(
                    "Immediately investigate server error logs. "
                    "Common causes: database errors, misconfigured server, "
                    "resource exhaustion, or code bugs. "
                    "Set up server monitoring and alerts."
                ),
                affected_element=url,
                page_url=url,
            )
        )

    # 3xx redirects
    if 300 <= status < 400 and redirect_url:
        issues.append(
            AuditIssue(
                issue_type="redirect_chain",
                category=IssueCategory.CRAWLABILITY,
                severity=IssueSeverity.MEDIUM,
                title=f"Page redirects ({status} → {redirect_url})",
                description=(
                    f"The page at {url} returns HTTP {status} and redirects to {redirect_url}. "
                    "Each redirect adds latency and may lose small amounts of ranking signals. "
                    "Chains of 2+ redirects are significantly worse."
                ),
                recommendation=(
                    f"If possible, update the source to redirect directly to the final destination. "
                    f"Point {url} directly at the final URL to eliminate the intermediate hop. "
                    "Use 301 (permanent) for content that moved permanently, 302 (temporary) otherwise."
                ),
                affected_element=f"HTTP {status} → {redirect_url}",
                page_url=url,
            )
        )

    # noindex detection
    if not is_indexable:
        issues.append(
            AuditIssue(
                issue_type="noindex_tag",
                category=IssueCategory.INDEXABILITY,
                severity=IssueSeverity.MEDIUM,
                title="Page has noindex directive",
                description=(
                    f"The page at {url} has a meta robots 'noindex' tag or X-Robots-Tag. "
                    "This page will not appear in search engine results. "
                    "Verify this is intentional — check if this is a page that should be indexed."
                ),
                recommendation=(
                    "If this page should be indexed (e.g., important landing pages, blog posts), "
                    "remove the noindex directive from the <meta robots> tag. "
                    "If the page should remain non-indexable (e.g., thank you pages, admin pages), "
                    "this is expected behavior."
                ),
                affected_element="<meta name='robots' content='noindex'>",
                page_url=url,
            )
        )

    # Thin content (very few words on non-nav pages)
    word_count = page.word_count or 0
    if word_count > 0 and word_count < 50:
        issues.append(
            AuditIssue(
                issue_type="thin_content",
                category=IssueCategory.INDEXABILITY,
                severity=IssueSeverity.MEDIUM,
                title=f"Thin content ({word_count} words)",
                description=(
                    f"This page has only {word_count} words of content. "
                    "Thin content provides little value to users and may be considered "
                    "low-quality by search engines, potentially harming site-wide rankings."
                ),
                recommendation=(
                    "Expand this page with meaningful content of at least 300 words. "
                    "If this is a navigation or utility page (e.g., login, cart), "
                    "consider adding a noindex directive to prevent thin-content penalties."
                ),
                affected_element="<body>",
                page_url=url,
            )
        )

    return issues
