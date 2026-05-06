# packages/seo-audit/analyzers/image_analyzer.py
"""Analyze images for missing alt text and accessibility issues."""

from ...crawler.models import PageRecord
from ...models import AuditIssue, IssueCategory, IssueSeverity


def analyze(page: PageRecord) -> list[AuditIssue]:
    """Analyze images on a page.

    Checks:
    - Presence of images without alt attributes
    - Images with empty alt attributes (accessibility issue)
    - Ratio of alt-missing images to total images
    - Decorative images (empty alt is valid for them)
    """
    issues: list[AuditIssue] = []
    images_count = page.images_count
    images_without_alt = page.images_without_alt

    if images_count == 0:
        return issues  # No images — nothing to check

    if images_without_alt > 0:
        pct = (images_without_alt / images_count) * 100
        severity = IssueSeverity.HIGH if pct > 30 else IssueSeverity.MEDIUM if pct > 10 else IssueSeverity.LOW

        issues.append(
            AuditIssue(
                issue_type="images_missing_alt_text",
                category=IssueCategory.METADATA,
                severity=severity,
                title=f"{images_without_alt}/{images_count} images missing alt text ({pct:.0f}%)",
                description=(
                    f"{images_without_alt} out of {images_count} images on this page "
                    f"are missing alt text ({pct:.0f}% non-compliant). "
                    "Alt text is required for screen readers (accessibility) and helps "
                    "search engines understand image content for image search and ranking."
                ),
                recommendation=(
                    "Add descriptive alt attributes to all informational images. "
                    "Use concise, keyword-relevant descriptions. "
                    "Decorative images should use alt='' (empty string, not missing). "
                    "Example: <img src='hero.jpg' alt='Blue widget product photo on white background'>"
                ),
                affected_element="<img> (missing alt)",
                page_url=page.url,
                count=images_without_alt,
            )
        )

    return issues
