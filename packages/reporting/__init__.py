"""SEO Agent OS — Reporting Package.

Converts audit results, crawl summaries, and content analysis into
human-readable reports (Markdown first, HTML/PDF later).

Public API:
    from .reporting import (
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

from .models import (
    ReportFormat,
    ReportType,
    ScoreCard,
    IssueRow,
    FixRecommendation,
    ReportMetadata,
    ReportData,
)
from .formatters import MarkdownFormatter
from .generators import (
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
