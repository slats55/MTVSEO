# SEO Agent OS — Reporting Package

Converts crawl results, SEO audit reports, and content analysis into human-readable Markdown reports.

**Format-agnostic design:** report generators produce a `ReportData` intermediate object, formatters turn it into a specific output format. HTML/PDF formatters can be added without changing generators.

---

## Architecture

```
packages/reporting/
  models.py              # ReportData, ScoreCard, IssueRow, FixRecommendation, enums
  formatters/
    markdown.py          # MarkdownFormatter → formatted Markdown string
  generators/
    audit_report.py      # AuditReportGenerator: seo_audit + crawl → ReportData
    crawl_summary.py     # CrawlSummaryGenerator: crawl_result → ReportData
    content_report.py    # ContentReportGenerator: PageRecord list → ReportData
  __init__.py           # Public API re-exports
  __main__.py           # CLI entry point
  README.md             # This file
```

---

## Public API

```python
from packages.reporting import (
    # Models
    ReportData, ReportMetadata, ReportType, ReportFormat,
    ScoreCard, IssueRow, FixRecommendation,
    # Formatters
    MarkdownFormatter,
    # Generators
    AuditReportGenerator,
    CrawlSummaryGenerator,
    ContentReportGenerator,
)
```

---

## Usage

### Library usage

```python
# Crawl summary report
from packages.reporting import CrawlSummaryGenerator, MarkdownFormatter

generator = CrawlSummaryGenerator()
report_data = generator.run(crawl_result, website_url="https://example.com")

formatter = MarkdownFormatter()
markdown = formatter.render(report_data)
print(markdown)
```

```python
# SEO audit report
from packages.reporting import AuditReportGenerator, MarkdownFormatter

generator = AuditReportGenerator()
report_data = generator.run(audit_report, crawl_result, website_url="https://example.com")

formatter = MarkdownFormatter()
print(formatter.render(report_data))
```

```python
# Content analysis report
from packages.reporting import ContentReportGenerator, MarkdownFormatter

generator = ContentReportGenerator()
report_data = generator.run(pages_list, website_url="https://example.com")
print(MarkdownFormatter().render(report_data))
```

### CLI usage

```bash
# Generate SEO audit report from a crawl result JSON
python -m packages.reporting audit crawl_result.json --output seo-report.md

# Generate crawl summary report
python -m packages.reporting crawl crawl_result.json -o crawl-report.md

# Generate content analysis report from pages JSON
python -m packages.reporting content pages.json --output content-report.md
```

---

## Report Format

Each report includes:

| Section | Description |
|---------|-------------|
| **Header** | Website URL, timestamp, pages crawled, duration |
| **Overall Score** | 0-100 score with letter grade and category breakdown table |
| **Executive Summary** | 2-3 sentence overview of findings |
| **Key Findings** | Bulleted list of top issues |
| **Issues Table** | All issues grouped by severity with URL, category, and recommendation |
| **Priority Fixes** | Sorted table of top fixes with estimated impact |
| **Supplemental Data** | Per-report extra tables (size distribution, word count, status codes, etc.) |
| **Footer** | Report generation timestamp |

---

## Score Breakdown

### Crawl Summary Scores
- **Crawl Coverage** (25%): Pages discovered vs target
- **Crawl Efficiency** (25%): Error rate (lower is better)
- **Page Quality** (25%): Average word count and page size
- **Crawl Health** (25%): Aggregate health metric

### Content Analysis Scores
- **Titles** (20%): Presence and length (30-60 chars)
- **Meta Descriptions** (15%): Presence and length (70-160 chars)
- **Headings** (15%): H1 presence and length
- **Content Quality** (25%): Word count vs 300-word minimum
- **Image Optimization** (15%): Alt text coverage
- **Readability** (10%): Word count as proxy

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `packages/crawler` | `PageRecord`, `CrawlResult` |
| `packages/seo-audit` | `AuditReport` (audit generator only) |
| `packages/shared` | Types, exceptions |
