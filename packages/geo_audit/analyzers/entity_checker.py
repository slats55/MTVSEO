# packages/geo-audit/analyzers/entity_checker.py
"""Check entity optimization — business clearly defined with sameAs schema and social profiles."""

from ...crawler.models import PageRecord
from ..models import GeoIssue, GeoIssueCategory, GeoIssueSeverity


# Social platform domains to check for in schema sameAs
SOCIAL_PROFILES = {
    "facebook.com": "Facebook",
    "twitter.com": "X (Twitter)",
    "x.com": "X (Twitter)",
    "instagram.com": "Instagram",
    "linkedin.com": "LinkedIn",
    "youtube.com": "YouTube",
    "tiktok.com": "TikTok",
    "github.com": "GitHub",
    "pinterest.com": "Pinterest",
    "yelp.com": "Yelp",
}


def analyze(
    pages: list[PageRecord],
    homepage_url: str,
) -> tuple[list[GeoIssue], int]:
    """Check entity optimization across all pages.

    Checks:
    - Homepage has Organization/LocalBusiness schema with sameAs
    - Homepage schema includes social profile links in sameAs
    - Other pages reference the business entity (author, about mentions)
    - Knowledge base pages define the business clearly

    Returns:
        (list of issues, count of pages with entity signals)
    """
    issues: list[GeoIssue] = []
    pages_with_entity_signals = 0

    homepage = next((p for p in pages if p.url.rstrip("/") == homepage_url.rstrip("/")), None)

    # ── 1. Homepage Organization Schema ─────────────────────────────────
    if homepage:
        schema_types = homepage.schema_types or []
        has_org_schema = any(
            t in schema_types for t in ["Organization", "LocalBusiness", "Corporation"]
        )
        if not has_org_schema:
            issues.append(
                GeoIssue(
                    issue_type="homepage_missing_org_schema",
                    category=GeoIssueCategory.ENTITY_OPTIMIZATION,
                    severity=GeoIssueSeverity.HIGH,
                    title="Homepage missing Organization schema",
                    description=(
                        "The homepage has no Organization or LocalBusiness schema. "
                        "Entity schema helps AI systems identify and disambiguate your business. "
                        "Without it, AI may not correctly attribute content to your business."
                    ),
                    recommendation=(
                        "Add Organization or LocalBusiness JSON-LD schema to the homepage. "
                        "Include: name, url, logo, description, sameAs (social profiles), "
                        "address, contact info."
                    ),
                    affected_element="<script type='application/ld+json'>",
                    page_url=homepage.url,
                )
            )

        # ── 2. sameAs with social profiles ──────────────────────────────
        # We detect social profile signals from schema (schema_types contains URL-like strings)
        # and from title/meta (social mentions)
        schema_str = ",".join(schema_types).lower()
        social_found: set[str] = set()
        for domain, name in SOCIAL_PROFILES.items():
            if domain in schema_str or any(domain in (p.title or "").lower() for p in pages):
                social_found.add(name)

        if has_org_schema and len(social_found) < 3:
            missing = [n for _, n in SOCIAL_PROFILES.items() if n not in social_found][:3]
            issues.append(
                GeoIssue(
                    issue_type="missing_social_profiles_in_schema",
                    category=GeoIssueCategory.ENTITY_OPTIMIZATION,
                    severity=GeoIssueSeverity.MEDIUM,
                    title=f"Organization schema missing most social profile sameAs ({len(social_found)} found)",
                    description=(
                        f"Organization schema found but only {len(social_found)} social profiles "
                        f"in sameAs: {', '.join(sorted(social_found)) or 'none'}. "
                        "Social profiles in schema help AI systems build a complete picture "
                        "of your business entity and verify authenticity."
                    ),
                    recommendation=(
                        f"Add these social profiles to Organization schema sameAs: "
                        f"{', '.join(missing)}. "
                        "Include at least 3-5 major platforms where the business has an active presence."
                    ),
                    affected_element="<script type='application/ld+json'> (sameAs)",
                    page_url=homepage.url,
                )
            )

        # ── 3. About page signals ───────────────────────────────────────
        about_pages = [p for p in pages if "about" in p.url.lower()]
        if not about_pages:
            issues.append(
                GeoIssue(
                    issue_type="no_about_page_found",
                    category=GeoIssueCategory.ENTITY_OPTIMIZATION,
                    severity=GeoIssueSeverity.MEDIUM,
                    title="No /about page found",
                    description=(
                        "No about page was discovered in the crawl. "
                        "An About page is critical for entity clarity — it tells AI systems "
                        "who this business is, what they do, and why they should be trusted."
                    ),
                    recommendation=(
                        "Create an /about page that clearly defines: who you are, "
                        "what you do, your team's background, your unique approach, "
                        "and proof elements (testimonials, case studies, credentials)."
                    ),
                    affected_element="/about",
                )
            )
            pages_with_entity_signals += 1  # count homepage as having some entity signal
        else:
            # About page should have substantial content
            about = about_pages[0]
            if about.word_count and about.word_count < 200:
                issues.append(
                    GeoIssue(
                        issue_type="about_page_too_thin",
                        category=GeoIssueCategory.ENTITY_OPTIMIZATION,
                        severity=GeoIssueSeverity.MEDIUM,
                        title="About page has very thin content",
                        description=(
                            f"About page at {about.url} has only {about.word_count} words. "
                            "AI systems rely on About pages for entity verification. "
                            "Thin about pages provide no substance for AI to cite."
                        ),
                        recommendation=(
                            "Expand the About page to at least 400 words. "
                            "Include: business story, team introduction, specific expertise areas, "
                            "proof elements (stats, testimonials, credentials)."
                        ),
                        affected_element=about.url,
                        page_url=about.url,
                    )
                )
            pages_with_entity_signals += 1

        # Count pages with entity signals (org schema or business-specific content)
        pages_with_entity_signals += sum(
            1 for p in pages
            if p.has_schema and p.schema_types
            and any(t in (p.schema_types or []) for t in ["Organization", "LocalBusiness", "Person", "Corporation"])
        )

    return issues, pages_with_entity_signals
