# packages/geo-audit/reporter.py
"""GeoAuditReporter — orchestrates all GEO analyzers and produces a GeoAuditReport."""

from collections import Counter
from urllib.parse import urlparse

from packages.crawler.models import CrawlResult, PageRecord
from packages.geo_audit.analyzers import (
    analyze_crawler_access,
    analyze_llms_txt,
    generate_llms_txt_draft,
    score_page_citability,
    analyze_entities,
    analyze_ai_readiness,
)
from packages.geo_audit.models import GeoIssue, GeoAuditReport, GeoIssueCategory, GeoIssueSeverity
from packages.geo_audit.scorer import compute_score


class GeoAuditReporter:
    """Orchestrates all GEO analyzers against a CrawlResult and produces a GeoAuditReport."""

    def __init__(self, domain: str, crawl_result: CrawlResult) -> None:
        self.domain = domain
        self.crawl = crawl_result
        self._issues: list[GeoIssue] = []

    def run(self, robots_txt_content: str | None = None) -> GeoAuditReport:
        """Run all GEO analyzers against crawled pages and return a GeoAuditReport."""
        pages = self.crawl.pages
        homepage_url = str(self.crawl.config.start_url).rstrip("/")

        # ── 1. AI Crawler Access ─────────────────────────────────────────
        self._issues.extend(analyze_crawler_access(robots_txt_content))

        # ── 2. llms.txt check ───────────────────────────────────────────
        # llms_txt_content would be fetched separately; pass None if not available
        llms_txt_content: str | None = None  # TODO: fetch /llms.txt separately
        self._issues.extend(analyze_llms_txt(llms_txt_content, self.domain, pages))
        llms_txt_found = llms_txt_content is not None

        # ── 3. Citability scoring per page ───────────────────────────────
        citability_scores: list[int] = []
        for page in pages:
            score, issues = score_page_citability(page)
            citability_scores.append(score)
            self._issues.extend(issues)

        avg_citability = sum(citability_scores) / len(citability_scores) if citability_scores else 0

        # ── 4. Entity optimization ──────────────────────────────────────
        entity_issues, pages_with_entity_signals = analyze_entities(pages, homepage_url)
        self._issues.extend(entity_issues)

        homepage = next((p for p in pages if p.url.rstrip("/") == homepage_url), None)
        homepage_has_org_schema = (
            homepage is not None
            and homepage.has_schema
            and any(t in (homepage.schema_types or []) for t in ["Organization", "LocalBusiness"])
        ) if homepage else False

        # ── 5. AI Answer Readiness ───────────────────────────────────────
        ai_issues, pages_with_ai_readiness = analyze_ai_readiness(pages)
        self._issues.extend(ai_issues)

        # ── 6. Compute score ─────────────────────────────────────────────
        pages_crawled = sum(1 for p in pages if p.status_code is not None)
        pages_with_proof_signals = sum(
            1 for p in pages if p.images_count > 0 and p.images_without_alt == 0
        )

        score = compute_score(
            issues=self._issues,
            pages_crawled=pages_crawled,
            pages_with_entity_signals=pages_with_entity_signals,
            pages_with_proof_signals=pages_with_proof_signals,
            llms_txt_found=llms_txt_found,
            homepage_has_org_schema=homepage_has_org_schema,
            avg_citability_score=avg_citability,
        )

        # ── 7. Group issues ──────────────────────────────────────────────
        by_severity: dict[GeoIssueSeverity, int] = {}
        by_category: dict[GeoIssueCategory, int] = {}
        for issue in self._issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
            by_category[issue.category] = by_category.get(issue.category, 0) + 1

        critical: list[str] = []
        high: list[str] = []
        medium: list[str] = []
        for issue in self._issues:
            rec = f"[{issue.severity.value}] {issue.title}: {issue.recommendation}"
            if issue.severity == GeoIssueSeverity.CRITICAL:
                critical.append(rec)
            elif issue.severity == GeoIssueSeverity.HIGH:
                high.append(rec)
            elif issue.severity == GeoIssueSeverity.MEDIUM:
                medium.append(rec)

        # ── 8. Generate llms.txt draft if missing ───────────────────────
        llms_txt_draft: str | None = None
        if not llms_txt_found:
            llms_txt_draft = generate_llms_txt_draft(self.domain, pages)

        report = GeoAuditReport(
            domain=self.domain,
            crawl_run_id=None,
            score=score,
            total_issues=len(self._issues),
            issues_by_severity=by_severity,
            issues_by_category=by_category,
            issues=self._issues,
            pages_audited=len(pages),
            llms_txt_found=llms_txt_found,
            homepage_has_organization_schema=homepage_has_org_schema,
            pages_with_entity_signals=pages_with_entity_signals,
            pages_with_proof_signals=pages_with_proof_signals,
            critical_fixes=critical[:10],
            high_priority_fixes=high[:10],
            medium_priority_fixes=medium[:10],
            llms_txt_draft=llms_txt_draft,
        )
        return report
