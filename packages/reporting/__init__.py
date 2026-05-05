"""SEO Agent OS — Reporting Package.

Converts audit results, crawl summaries, and content analysis into
human-readable reports (Markdown first, HTML/PDF later).

Public API:
    from packages.reporting import (
        MarkdownFormatter,
        AuditReportGenerator,
        CrawlSummaryGenerator,
        ContentReportGenerator,
        ReportData,
        ReportType,
        ReportFormat,
        ScoreCard,
        IssueRow,
        FixRecommendation,
    )

Usage:
    # From a crawl result
    generator = CrawlSummaryGenerator()
    report_data = generator.run(crawl_result, website_url="https://example.com")

    # Render as Markdown
    formatter = MarkdownFormatter()
    markdown = formatter.render(report_data)
    print(markdown)
"""  

from packages.reporting.models import (
    ReportFormat,
    ReportType,
    ScoreCard,
    IssueRow,
    FixRecommendation,
    ReportMetadata,
    ReportData,
)
from packages.reporting.formatters import MarkdownFormatter
from packages.reporting.generators import (
    AuditReportGenerator,
    CrawlSummaryGenerator,
    ContentReportGenerator,
)

__all__ = [
    # Models
    "ReportFormat",
    "ReportType",
    "ScoreCard",
    "IssueRow",
    "FixRecommendation",
    "ReportMetadata",
    "ReportData",
    # Formatters
    "MarkdownFormatter",
    # Generators
    "AuditReportGenerator",
    "CrawlSummaryGenerator",
    "ContentReportGenerator",
]
