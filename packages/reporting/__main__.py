"""CLI entry point for packages/reporting.

Usage:
    python -m packages.reporting audit <crawl_result.json> [--output report.md]
    python -m packages.reporting crawl <crawl_result.json> [--output report.md]
    python -m packages.reporting content <pages.json> [--output report.md]

Examples:
    python -m packages.reporting audit crawl_result.json --output seo-report.md
    python -m packages.reporting crawl crawl_result.json --format markdown
    python -m packages.reporting content pages.json --output content-report.md
"""

import argparse
import json
import sys
from pathlib import Path

from packages.reporting import (
    MarkdownFormatter,
    AuditReportGenerator,
    CrawlSummaryGenerator,
    ContentReportGenerator,
    ReportType,
)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_audit(input_path: str, output_path: str | None) -> None:
    data = load_json(input_path)

    # Support both raw crawl_result and wrapped {crawl_result, seo_audit} formats
    crawl_result_data = data.get("crawl_result", data)
    audit_report_data = data.get("seo_audit", {})

    # Deserialize into Pydantic models
    from packages.crawler.models import CrawlResult
    from packages.seo_audit.models import AuditReport

    crawl_result = CrawlResult.model_validate(crawl_result_data)
    audit_report = AuditReport.model_validate(audit_report_data) if audit_report_data else None

    website_url = data.get("website_url", crawl_result.start_url)

    generator = AuditReportGenerator()
    if audit_report:
        report_data = generator.run(audit_report, crawl_result, website_url)
    else:
        # No seo_audit data — skip to crawl summary
        cg = CrawlSummaryGenerator()
        report_data = cg.run(crawl_result, website_url)

    formatter = MarkdownFormatter()
    output = formatter.render(report_data)

    if output_path:
        Path(output_path).write_text(output, encoding="utf-8")
        print(f"Report written to {output_path}")
    else:
        print(output)


def run_crawl(input_path: str, output_path: str | None) -> None:
    data = load_json(input_path)
    from packages.crawler.models import CrawlResult
    crawl_result = CrawlResult.model_validate(data.get("crawl_result", data))
    website_url = data.get("website_url", crawl_result.start_url)

    generator = CrawlSummaryGenerator()
    report_data = generator.run(crawl_result, website_url)

    formatter = MarkdownFormatter()
    output = formatter.render(report_data)

    if output_path:
        Path(output_path).write_text(output, encoding="utf-8")
        print(f"Report written to {output_path}")
    else:
        print(output)


def run_content(input_path: str, output_path: str | None) -> None:
    data = load_json(input_path)
    from packages.crawler.models import PageRecord
    pages_data = data.get("pages", data) if isinstance(data, dict) else data
    pages = [PageRecord.model_validate(p) for p in pages_data]
    website_url = data.get("website_url", "https://unknown")

    generator = ContentReportGenerator()
    report_data = generator.run(pages, website_url)

    formatter = MarkdownFormatter()
    output = formatter.render(report_data)

    if output_path:
        Path(output_path).write_text(output, encoding="utf-8")
        print(f"Report written to {output_path}")
    else:
        print(output)


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m packages.reporting")
    parser.add_argument(
        "report_type",
        choices=["audit", "crawl", "content"],
        help="Type of report to generate",
    )
    parser.add_argument("input", help="Input JSON file path")
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    if args.report_type == "audit":
        run_audit(args.input, args.output)
    elif args.report_type == "crawl":
        run_crawl(args.input, args.output)
    elif args.report_type == "content":
        run_content(args.input, args.output)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
