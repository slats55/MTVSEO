# packages/seo-audit/analyzers/__init__.py
"""Individual SEO check analyzers.

Each module exposes an analyze() function that takes a PageRecord and returns
a list of AuditIssue objects found on that page.
"""

from packages.seo_audit.analyzers.title_analyzer import analyze as analyze_titles
from packages.seo_audit.analyzers.meta_analyzer import analyze as analyze_meta
from packages.seo_audit.analyzers.heading_analyzer import analyze as analyze_headings
from packages.seo_audit.analyzers.canonical_analyzer import analyze as analyze_canonical
from packages.seo_audit.analyzers.schema_analyzer import analyze as analyze_schema
from packages.seo_audit.analyzers.image_analyzer import analyze as analyze_images
from packages.seo_audit.analyzers.link_analyzer import analyze as analyze_links
from packages.seo_audit.analyzers.tech_analyzer import analyze as analyze_tech

__all__ = [
    "analyze_titles",
    "analyze_meta",
    "analyze_headings",
    "analyze_canonical",
    "analyze_schema",
    "analyze_images",
    "analyze_links",
    "analyze_tech",
]
