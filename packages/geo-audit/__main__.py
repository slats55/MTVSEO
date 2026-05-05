# packages/geo-audit/__main__.py
"""CLI entry point: python -m packages.geo_audit <crawl_result_json> [--robots robots.txt]"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from packages.crawler.models import CrawlResult
from packages.geo_audit.reporter import GeoAuditReporter
from packages.geo_audit import __version__


def main() -> None:
    parser = argparse.ArgumentParser(description="SEO Agent OS — GEO / AI Visibility Audit")
    parser.add_argument("crawl_result", help="Path to CrawlResult JSON file (from crawler)")
    parser.add_argument("--robots", dest="robots_txt", help="Path to robots.txt file content")
    parser.add_argument("--domain", help="Domain override")
    parser.add_argument("--output", "-o", help="Output path for JSON report")
    args = parser.parse_args()

    # Load crawl result
    with open(args.crawl_result) as f:
        data = json.load(f)
    crawl_result = CrawlResult.model_validate(data)

    domain = args.domain or crawl_result.config.domain or "unknown"
    robots_txt = None
    if args.robots_txt:
        with open(args.robots_txt) as f:
            robots_txt = f.read()

    reporter = GeoAuditReporter(domain, crawl_result)
    report = reporter.run(robots_txt_content=robots_txt)

    print("\n=== GEO / AI Visibility Audit ===")
    print(f"  Domain:   {report.domain}")
    print(f"  Score:    {report.score.total:.0f}/100 ({report.score.grade()})")
    print(f"  Issues:   {report.total_issues}")
    print(f"  Audited:  {report.pages_audited} pages")
    print(f"  llms.txt: {'Found' if report.llms_txt_found else 'Missing (draft generated)'}")
    print(f"\n=== Category Breakdown ===")
    print(f"  AI Crawler Access:     {report.score.ai_crawler_access:.1f}/15")
    print(f"  Entity Clarity:        {report.score.entity_clarity:.1f}/15")
    print(f"  Citability:            {report.score.citability:.1f}/25")
    print(f"  Content Depth:         {report.score.content_depth:.1f}/20")
    print(f"  Schema:                {report.score.schema:.1f}/10")
    print(f"  Brand Authority:       {report.score.brand_authority:.1f}/10")
    print(f"  LLM Readability:       {report.score.llm_readability:.1f}/5")
    print(f"\n=== Issues by Severity ===")
    for sev in GeoIssueSeverity:
        count = report.issues_by_severity.get(sev, 0)
        if count:
            print(f"  {sev.value}: {count}")

    if report.issues:
        print(f"\n=== Top Issues ===")
        for issue in report.issues[:10]:
            print(f"  [{issue.severity.value}] {issue.title}")
            print(f"    → {issue.recommendation}")

    if report.llms_txt_draft:
        draft_path = Path(f"{domain}-llms.txt")
        draft_path.write_text(report.llms_txt_draft)
        print(f"\n=== llms.txt draft written to: {draft_path} ===")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report.model_dump(mode="json"), f, indent=2, default=str)
        print(f"\nFull report saved to: {args.output}")


if __name__ == "__main__":
    main()
