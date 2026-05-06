# packages/geo-audit/analyzers/__init__.py
"""Individual GEO audit analyzers.

Each module exposes an analyze() function that takes a PageRecord (from crawler)
and returns a list of GeoIssue objects.
"""

from ...analyzers.crawler_checker import analyze as analyze_crawler_access
from ...analyzers.llms_generator import generate_llms_txt_draft, analyze_llms_txt
from ...analyzers.citability_scorer import score_page_citability
from ...analyzers.entity_checker import analyze as analyze_entities
from ...analyzers.ai_readiness_checker import analyze as analyze_ai_readiness

__all__ = [
    "analyze_crawler_access",
    "generate_llms_txt_draft",
    "analyze_llms_txt",
    "score_page_citability",
    "analyze_entities",
    "analyze_ai_readiness",
]
