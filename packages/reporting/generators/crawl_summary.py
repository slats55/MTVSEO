"""Crawl summary report generator.

Converts a CrawlResult / CrawlSummary (from packages/crawler) into
a ReportData intermediate representation.
"""

from datetime import datetime, timezone
from packages.crawler.models import CrawlResult, CrawlSummary, PageRecord
from packages.reporting.models import (
    ReportData,
    ReportMetadata,
    ReportType,
    ScoreCard,
    IssueRow,
    FixRecommendation,
)


# Size buckets for distribution reporting
_SIZE_BUCKETS = [
    (0, 10, "Under 10KB"),
    (10, 50, "10-50KB"),
    (50, 200, "50-200KB"),
    (200, 500, "200-500KB"),
    (500, float("inf"), "Over 500KB"),
]

# Word count buckets
_WORD_BUCKETS = [
    (0, 100, "Thin (<100 words)"),
    (100, 300, "Short (100-300)"),
    (300, 1000, "Medium (300-1000)"),
    (1000, float("inf"), "Long (1000+)"),
]


class CrawlSummaryGenerator:
    """Converts a crawler CrawlResult → ReportData (no DB, no audit)."""

    def run(
        self,
        crawl_result: CrawlResult,
        website_url: str,
    ) -> ReportData:
        """Build a ReportData from a crawler CrawlResult."""
        summary = crawl_result.summary if crawl_result.summary else self._build_summary(crawl_result)
        meta = ReportMetadata(
            website_url=website_url,
            report_type=ReportType.CRAWL_SUMMARY,
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_pages_crawled=summary.pages_crawled if summary else len(crawl_result.pages),
            crawl_duration_seconds=summary.duration_seconds if summary else 0.0,
        )

        # Compute a crawl health score (0-100)
        health_score = self._compute_health_score(crawl_result)
        health_grade = self._score_to_grade(health_score)

        score_breakdown = [
            ScoreCard(
                label="Crawl Coverage",
                score=self._coverage_score(crawl_result),
                weight=0.25,
                grade=self._score_to_grade(self._coverage_score(crawl_result)),
                issues_count=0,
            ),
            ScoreCard(
                label="Crawl Efficiency",
                score=self._efficiency_score(crawl_result),
                weight=0.25,
                grade=self._score_to_grade(self._efficiency_score(crawl_result)),
                issues_count=0,
            ),
            ScoreCard(
                label="Page Quality",
                score=self._quality_score(crawl_result),
                weight=0.25,
                grade=self._score_to_grade(self._quality_score(crawl_result)),
                issues_count=0,
            ),
            ScoreCard(
                label="Crawl Health",
                score=health_score,
                weight=0.25,
                grade=health_grade,
                issues_count=0,
            ),
        ]

        overall = health_score  # simplified — no separate scoring
        key_findings = self._build_findings(crawl_result, summary)
        issues = self._build_issues(crawl_result)
        fixes = self._build_fixes(crawl_result, issues)
        summary_text = self._build_summary_text(crawl_result, summary)
        supplemental = self._build_supplemental(crawl_result, summary)

        return ReportData(
            metadata=meta,
            overall_score=overall,
            overall_grade=health_grade,
            score_breakdown=score_breakdown,
            issues=issues,
            fixes=fixes,
            summary_text=summary_text,
            key_findings=key_findings,
            supplemental=supplemental,
        )

    def _build_summary(self, result: CrawlResult) -> CrawlSummary:
        """Fallback if no CrawlSummary attached."""
        pages = result.pages
        total_size = sum(p.raw_content_size or 0 for p in pages)
        return CrawlSummary(
            pages_crawled=len(pages),
            pages_failed=sum(1 for p in pages if p.status_code >= 400),
            total_urls_discovered=len(pages),
            total_urls_crawled=len(pages),
            duration_seconds=0.0,
            start_time=datetime.now(timezone.utc).isoformat(),
            end_time=datetime.now(timezone.utc).isoformat(),
            average_page_size=total_size / len(pages) if pages else 0,
            average_word_count=int(sum(p.word_count or 0 for p in pages) / len(pages)) if pages else 0,
        )

    # ---------------------------------------------------------------------------
    # Score helpers
    # ---------------------------------------------------------------------------

    def _coverage_score(self, result: CrawlResult) -> float:
        """Higher is better: reward pages discovered vs pages crawled."""
        pages = result.pages
        if not pages:
            return 0.0
        discovered = len(pages)
        # Penalize if we hit max_pages limit
        return min(100.0, (discovered / 25) * 100)

    def _efficiency_score(self, result: CrawlResult) -> float:
        """Lower failed pages = higher score."""
        pages = result.pages
        if not pages:
            return 0.0
        failed = sum(1 for p in pages if p.status_code >= 400)
        rate = failed / len(pages)
        return max(0.0, 100.0 - rate * 100)

    def _quality_score(self, result: CrawlResult) -> float:
        """Based on average word count and page size."""
        pages = result.pages
        if not pages:
            return 0.0
        avg_words = sum(p.word_count or 0 for p in pages) / len(pages)
        avg_size = sum(p.raw_content_size or 0 for p in pages) / len(pages)
        word_score = min(100.0, (avg_words / 500) * 100)
        size_score = min(100.0, (avg_size / 50000) * 100)
        return (word_score * 0.6 + size_score * 0.4)

    def _compute_health_score(self, result: CrawlResult) -> float:
        """Aggregate of efficiency + coverage + quality."""
        return (
            self._coverage_score(result) * 0.2
            + self._efficiency_score(result) * 0.4
            + self._quality_score(result) * 0.4
        )

    @staticmethod
    def _score_to_grade(score: float) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"

    # ---------------------------------------------------------------------------
    # Issue / fix helpers
    # ---------------------------------------------------------------------------

    def _build_issues(self, result: CrawlResult) -> list[IssueRow]:
        issues = []
        pages = result.pages
        for page in pages:
            # Broken pages
            if page.status_code == 404:
                issues.append(
                    IssueRow(
                        severity="high",
                        category="Crawlability",
                        title="404 page found",
                        url=page.url,
                        description=f"Page returned HTTP 404.",
                        recommendation="Restore the page or set up a 301 redirect.",
                    )
                )
            elif page.status_code >= 500:
                issues.append(
                    IssueRow(
                        severity="high",
                        category="Crawlability",
                        title=f"Server error ({page.status_code})",
                        url=page.url,
                        description=f"Page returned HTTP {page.status_code}.",
                        recommendation="Check server logs and fix the error.",
                    )
                )
            # Thin content
            if page.word_count is not None and page.word_count < 100:
                issues.append(
                    IssueRow(
                        severity="medium",
                        category="Content Quality",
                        title="Thin content page",
                        url=page.url,
                        description=f"Page has only {page.word_count} words.",
                        recommendation="Expand content to at least 300 words for SEO benefit.",
                    )
                )
            # Missing title
            if not page.title:
                issues.append(
                    IssueRow(
                        severity="high",
                        category="On-Page SEO",
                        title="Missing page title",
                        url=page.url,
                        description="Page has no <title> tag.",
                        recommendation="Add a unique, descriptive <title> tag.",
                    )
                )
            # Missing meta description
            if not page.meta_description:
                issues.append(
                    IssueRow(
                        severity="medium",
                        category="On-Page SEO",
                        title="Missing meta description",
                        url=page.url,
                        description="Page has no meta description.",
                        recommendation="Add a meta description of 120-160 characters.",
                    )
                )
        return issues

    def _build_fixes(self, result: CrawlResult, issues: list[IssueRow]) -> list[FixRecommendation]:
        fixes: dict[str, FixRecommendation] = {}
        for issue in issues:
            if issue.severity not in ("critical", "high"):
                continue
            if issue.title not in fixes:
                fixes[issue.title] = FixRecommendation(
                    priority=1 if issue.severity == "critical" else 2,
                    title=issue.title,
                    description=issue.recommendation or issue.description,
                    url=issue.url,
                )
        return sorted(fixes.values(), key=lambda f: (f.priority, f.title))

    # ---------------------------------------------------------------------------
    # Findings / summary helpers
    # ---------------------------------------------------------------------------

    def _build_findings(self, result: CrawlResult, summary) -> list[str]:
        pages = result.pages
        findings = []
        total = len(pages)
        if total == 0:
            findings.append("No pages were crawled.")
            return findings
        failed = sum(1 for p in pages if p.status_code >= 400)
        if failed > 0:
            findings.append(f"{failed}/{total} pages returned error status codes.")
        thin = sum(1 for p in pages if (p.word_count or 0) < 100)
        if thin > 0:
            findings.append(f"{thin} page(s) have thin content (<100 words).")
        no_title = sum(1 for p in pages if not p.title)
        if no_title > 0:
            findings.append(f"{no_title} page(s) are missing title tags.")
        no_desc = sum(1 for p in pages if not p.meta_description)
        if no_desc > 0:
            findings.append(f"{no_desc} page(s) are missing meta descriptions.")
        return findings

    def _build_summary_text(self, result: CrawlResult, summary) -> str:
        pages = result.pages
        total = len(pages)
        if total == 0:
            return "No pages were crawled. Check the start URL and robots.txt settings."
        failed = sum(1 for p in pages if p.status_code >= 400)
        avg_words = int(sum(p.word_count or 0 for p in pages) / total) if total else 0
        return (
            f"Crawl of {result.start_url} collected {total} page(s) "
            f"with an average of {avg_words} words per page. "
            f"{failed} page(s) returned error status codes."
        )

    def _build_supplemental(self, result: CrawlResult, summary) -> dict[str, str]:
        pages = result.pages
        if not pages:
            return {}

        # Page size distribution
        size_lines = ["| Size Range | Count |", "|:-----------|------:|"]
        for lo, hi, label in _SIZE_BUCKETS:
            count = sum(1 for p in pages if (lo * 1024) <= (p.raw_content_size or 0) < (hi * 1024))
            if count:
                size_lines.append(f"| {label} | {count} |")

        # Word count distribution
        word_lines = ["| Content Length | Count |", "|:---------------|------:|"]
        for lo, hi, label in _WORD_BUCKETS:
            count = sum(1 for p in pages if lo <= (p.word_count or 0) < hi)
            if count:
                word_lines.append(f"| {label} | {count} |")

        # Status code distribution
        status_lines = ["| Status | Count |", "|:-------|------:|"]
        status_counts: dict[int, int] = {}
        for p in pages:
            status_counts[p.status_code] = status_counts.get(p.status_code, 0) + 1
        for code in sorted(status_counts):
            status_lines.append(f"| {code} | {status_counts[code]} |")

        return {
            "Page Size Distribution": "\n".join(size_lines),
            "Content Length Distribution": "\n".join(word_lines),
            "HTTP Status Distribution": "\n".join(status_lines),
        }
