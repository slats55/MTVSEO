# packages/seo-audit/analyzers/__init__.py
"""Individual SEO check analyzers.

Each module exposes an analyze() function that takes a PageRecord and returns
a list of AuditIssue objects found on that page.
"""

from ...analyzers.title_analyzer import analyze as analyze_titles
from ...analyzers.meta_analyzer import analyze as analyze_meta
from ...analyzers.heading_analyzer import analyze as analyze_headings
from ...analyzers.canonical_analyzer import analyze as analyze_canonical
from ...analyzers.schema_analyzer import analyze as analyze_schema
from ...analyzers.image_analyzer import analyze as analyze_images
from ...analyzers.link_analyzer import analyze as analyze_links
from ...analyzers.tech_analyzer import analyze as analyze_tech

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
