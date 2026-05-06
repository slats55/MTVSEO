# packages/seo-audit/reporter.py
"""AuditReporter — orchestrates all analyzers and produces an AuditReport."""

from collections import Counter
from urllib.parse import urlparse

from ..crawler.models import CrawlResult, PageRecord
from ..models import (
    AuditIssue,
    AuditReport,
    AuditScore,
    IssueCategory,
    IssueSeverity,
)
from ..scorer import compute_score


class AuditReporter:
    """Orchestrates all analyzers against a CrawlResult and produces an AuditReport."""

    def __init__(self, domain: str, crawl_result: CrawlResult) -> None:
        self.domain = domain
        self.crawl = crawl_result
        self._issues: list[AuditIssue] = []

    def run(self) -> AuditReport:
        """Run all analyzers against all crawled pages and return an AuditReport."""
        pages = self.crawl.pages

        # Build site-wide lookup maps for duplicate detection
        all_titles = Counter(
            p.title.lower().strip() for p in pages if p.title
        )
        all_descriptions = Counter(
            p.meta_description.lower().strip() for p in pages if p.meta_description
        )
        h1_counts: Counter[str] = Counter()
        h2_counts: Counter[str] = Counter()
        for p in pages:
            if p.h1:
                h1_counts[p.h1.lower().strip()] += 1
            for h2 in (p.h2_headings or []):
                h2_counts[h2.lower().strip()] += 1

        # Determine homepage URL for schema checks
        homepage_url = str(self.crawl.config.start_url).rstrip("/")

        # Run analyzers on each page
        for page in pages:
            is_homepage = page.url.rstrip("/") == homepage_url
            self._run_page_analyzers(page, all_titles, all_descriptions, h1_counts, h2_counts, is_homepage)

        # Compute aggregate metrics
        pages_crawled = sum(1 for p in pages if p.status_code is not None)
        pages_with_schema = sum(1 for p in pages if p.has_schema)
        pages_indexable = sum(1 for p in pages if p.is_indexable)
        pages_4xx = sum(1 for p in pages if p.status_code and 400 <= p.status_code < 500)
        pages_5xx = sum(1 for p in pages if p.status_code and p.status_code >= 500)
        homepage_has_schema = any(
            p.has_schema for p in pages if p.url.rstrip("/") == homepage_url
        )

        # Compute score
        score = compute_score(
            issues=self._issues,
            pages_discovered=len(pages),
            pages_crawled=pages_crawled,
            pages_with_schema=pages_with_schema,
            pages_indexable=pages_indexable,
            pages_4xx=pages_4xx,
            pages_5xx=pages_5xx,
            homepage_has_schema=homepage_has_schema,
        )

        # Group issues by severity and category
        by_severity: dict[IssueSeverity, int] = {}
        by_category: dict[IssueCategory, int] = {}
        for issue in self._issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
            by_category[issue.category] = by_category.get(issue.category, 0) + 1

        # Group fix recommendations by priority
        critical: list[str] = []
        high: list[str] = []
        medium: list[str] = []
        for issue in self._issues:
            rec = f"[{issue.severity.value}] {issue.title}: {issue.recommendation}"
            if issue.severity == IssueSeverity.CRITICAL:
                critical.append(rec)
            elif issue.severity == IssueSeverity.HIGH:
                high.append(rec)
            elif issue.severity == IssueSeverity.MEDIUM:
                medium.append(rec)

        # Count pages with critical issues
        pages_with_critical = sum(
            1 for url, group in self._group_by_page().items()
            if any(i.severity == IssueSeverity.CRITICAL for i in group)
        )

        # Duplicate counts
        dup_titles = sum(1 for c in all_titles.values() if c > 1)
        dup_descs = sum(1 for c in all_descriptions.values() if c > 1)

        report = AuditReport(
            domain=self.domain,
            crawl_run_id=None,
            score=score,
            total_issues=len(self._issues),
            issues_by_severity=by_severity,
            issues_by_category=by_category,
            issues=self._issues,
            pages_audited=len(pages),
            pages_with_critical_issues=pages_with_critical,
            pages_with_noindex=sum(1 for p in pages if not p.is_indexable),
            duplicate_title_count=dup_titles,
            duplicate_meta_desc_count=dup_descs,
            critical_fixes=critical[:10],      # top 10
            high_priority_fixes=high[:10],
            medium_priority_fixes=medium[:10],
        )
        return report

    def _run_page_analyzers(
        self,
        page: PageRecord,
        all_titles: Counter[str],
        all_descriptions: Counter[str],
        h1_counts: Counter[str],
        h2_counts: Counter[str],
        is_homepage: bool,
    ) -> None:
        """Run all analyzers against a single page."""
        # Lazy import to avoid circular dependency
        from ..analyzers import (
            analyze_titles, analyze_meta, analyze_headings,
            analyze_canonical, analyze_schema, analyze_images,
            analyze_links, analyze_tech,
        )

        # title_analyzer needs the full site-wide title map
        self._issues.extend(analyze_titles(page, dict(all_titles)))

        # meta_analyzer needs the full site-wide description map
        self._issues.extend(analyze_meta(page, dict(all_descriptions)))

        # heading_analyzer needs h1 count and h2 counts
        h1_text = (page.h1 or "").lower().strip()
        h1_count = h1_counts.get(h1_text, 0)
        self._issues.extend(analyze_headings(page, h1_count, dict(h2_counts)))

        # canonical, schema, image, link, tech analyzers
        self._issues.extend(analyze_canonical(page))
        self._issues.extend(analyze_schema(page, is_homepage=is_homepage))
        self._issues.extend(analyze_images(page))
        self._issues.extend(analyze_links(page))
        self._issues.extend(analyze_tech(page))

    def _group_by_page(self) -> dict[str, list[AuditIssue]]:
        """Group issues by page URL."""
        groups: dict[str, list[AuditIssue]] = {}
        for issue in self._issues:
            url = issue.page_url or ""
            if url not in groups:
                groups[url] = []
            groups[url].append(issue)
        return groups
