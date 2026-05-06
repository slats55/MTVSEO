# packages/seo-audit/analyzers/schema_analyzer.py
"""Analyze structured data (JSON-LD schema.org) for presence and validity."""

from urllib.parse import urlparse

from ...crawler.models import PageRecord
from ...models import AuditIssue, IssueCategory, IssueSeverity

PRIMARY_SCHEMA_TYPES = {
    "Organization", "LocalBusiness", "WebSite", "BreadcrumbList",
    "Service", "FAQPage", "Article", "Product", "Recipe", "Event",
}


def analyze(page: PageRecord, is_homepage: bool = False) -> list[AuditIssue]:
    """Analyze structured data on a page.

    Checks:
    - Presence of JSON-LD structured data
    - Recommended schema types for the page type
    - Organization/WebSite schema on homepage
    """
    issues: list[AuditIssue] = []
    schema_types = page.schema_types or []
    has_schema = page.has_schema

    if not has_schema or not schema_types:
        expected = "Organization, WebSite" if is_homepage else "At least one relevant schema.org type"
        issues.append(
            AuditIssue(
                issue_type="missing_schema",
                category=IssueCategory.STRUCTURED_DATA,
                severity=IssueSeverity.MEDIUM,
                title="No structured data found",
                description=(
                    f"This page has no JSON-LD structured data. Structured data helps "
                    "search engines understand page content and can enable rich results "
                    "(People Also Ask, rich snippets, Knowledge Panel, etc.). "
                    f"Expected types for this page: {expected}."
                ),
                recommendation=(
                    f"Add relevant JSON-LD structured data. For this page, consider adding: "
                    f"{expected}. Use Google's Rich Results Test to validate after implementation."
                ),
                affected_element="<script type='application/ld+json'>",
                page_url=page.url,
            )
        )
        return issues

    # Homepage-specific checks
    if is_homepage:
        homepage_types = {"Organization", "LocalBusiness", "WebSite", "SearchAction", "SiteNavigationElement"}
        found_homepage = set(schema_types) & homepage_types
        if not found_homepage:
            issues.append(
                AuditIssue(
                    issue_type="homepage_missing_core_schema",
                    category=IssueCategory.STRUCTURED_DATA,
                    severity=IssueSeverity.MEDIUM,
                    title="Homepage missing Organization/WebSite schema",
                    description=(
                        "The homepage should include Organization or LocalBusiness schema "
                        "and WebSite schema with a SearchAction to support brand Knowledge Panel "
                        "and sitelinks search box features."
                    ),
                    recommendation=(
                        "Add Organization or LocalBusiness schema with name, url, logo, "
                        "and contact information. Also add WebSite schema with SiteNavigationElement "
                        "and SearchAction for search box support."
                    ),
                    affected_element="<script type='application/ld+json'>",
                    page_url=page.url,
                )
            )

    # Context-aware type checks
    expected_types: set[str] = set()
    if page.title:
        title_lower = page.title.lower()
        if any(k in title_lower for k in ["faq", "question", "q&a"]):
            expected_types.add("FAQPage")
        if any(k in title_lower for k in ["about"]):
            expected_types.add("AboutPage")
        if any(k in title_lower for k in ["contact"]):
            expected_types.add("ContactPage")

    missing_types = expected_types - set(schema_types)
    if missing_types:
        issues.append(
            AuditIssue(
                issue_type="missing_recommended_schema_type",
                category=IssueCategory.STRUCTURED_DATA,
                severity=IssueSeverity.LOW,
                title=f"Missing recommended schema types: {', '.join(sorted(missing_types))}",
                description=(
                    f"Based on the page title '{page.title}', this page may benefit from "
                    f"the following schema types that weren't found: {', '.join(sorted(missing_types))}."
                ),
                recommendation=(
                    f"Add {', '.join(sorted(missing_types))} structured data to this page "
                    "to increase chances of rich result eligibility."
                ),
                affected_element="<script type='application/ld+json'>",
                page_url=page.url,
            )
        )

    return issues
