# packages/geo-audit — GEO / AI Visibility Analyzer.
#
# Public API:
#   GeoScore         — per-category and total GEO score (0-100)
#   GeoIssue         — single GEO issue
#   GeoAuditReport   — full GEO audit report
#   GeoAuditReporter — main orchestrator (run() → GeoAuditReport)
#   GeoIssueSeverity, GeoIssueCategory — enums
#
# Usage:
#   from packages.geo_audit import GeoAuditReporter
#   reporter = GeoAuditReporter(domain, crawl_result)
#   report = reporter.run(robots_txt_content=robots_txt_content)

from packages.geo_audit.models import (
    GeoScore,
    GeoIssue,
    GeoAuditReport,
    GeoIssueSeverity,
    GeoIssueCategory,
)
from packages.geo_audit.reporter import GeoAuditReporter

__all__ = [
    "GeoScore",
    "GeoIssue",
    "GeoAuditReport",
    "GeoAuditReporter",
    "GeoIssueSeverity",
    "GeoIssueCategory",
]
