"""Technical SEO audit report generator.

Converts an AuditReport (from packages/seo-audit) into a ReportData
intermediate representation suitable for any output formatter.
"""

from datetime import datetime, timezone
from ...seo_audit.models import AuditReport, AuditIssue, AuditScore
from ...seo_audit.scorer import compute_score
from ...reporting.models import (
    ReportData,
    ReportMetadata,
    ReportType,
    ScoreCard,
    IssueRow,
    FixRecommendation,
)


# Mapping from seo-audit categories to display labels
_CATEGORY_LABELS = {
    "crawlability": "Crawlability",
    "indexability": "Indexability",
    "metadata": "On-Page SEO",
    "content": "Content Quality",
    "images": "Images & Media",
    "links": "Links & Navigation",
    "structured_data": "Structured Data",
    "performance": "Performance",
    "security": "Security",
}


def _severity_weight(s: str) -> int:
    weights = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
    return weights.get(s.lower(), 0)


class AuditReportGenerator:
    """Converts a packages/seo-audit AuditReport → ReportData."""

    def run(
        self,
        audit_report: AuditReport,
        crawl_report,
        website_url: str,
    ) -> ReportData:
        """Build a ReportData from an seo-audit AuditReport and crawl result."""
        meta = ReportMetadata(
            website_url=website_url,
            report_type=ReportType.TECHNICAL_SEO,
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_pages_crawled=getattr(crawl_report, "pages_crawled", 0)
            if crawl_report
            else 0,
            crawl_duration_seconds=getattr(crawl_report, "duration_seconds", 0.0)
            if crawl_report
            else 0.0,
        )

        # Compute overall score
        overall = compute_score(audit_report.issues)
        overall_grade = _score_to_grade(overall)

        # Build score breakdown per category
        score_breakdown = _build_score_breakdown(audit_report)

        # Convert issues
        issues = [_issue_to_row(i) for i in audit_report.issues]

        # Build priority fixes from critical/high issues
        fixes = _build_fixes(audit_report.issues)

        # Key findings
        key_findings = _build_findings(audit_report, overall)

        # Summary
        summary = _build_summary(audit_report, overall)

        return ReportData(
            metadata=meta,
            overall_score=overall,
            overall_grade=overall_grade,
            score_breakdown=score_breakdown,
            issues=issues,
            fixes=fixes,
            summary_text=summary,
            key_findings=key_findings,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _score_to_grade(score: float) -> str:
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


def _build_score_breakdown(audit_report: AuditReport) -> list[ScoreCard]:
    """Compute per-category scores from issue distribution."""
    # Default weights matching seo-audit/scorer.py
    weights = {
        "crawlability": 0.20,
        "indexability": 0.20,
        "metadata": 0.20,
        "content": 0.10,
        "images": 0.05,
        "links": 0.10,
        "structured_data": 0.10,
        "performance": 0.03,
        "security": 0.02,
    }
    # Distribute issues into categories
    cat_issues: dict[str, list[AuditIssue]] = {}
    for issue in audit_report.issues:
        cat = issue.category.value if hasattr(issue.category, "value") else issue.category
        cat_issues.setdefault(cat, []).append(issue)

    cards = []
    for cat, cat_issue_list in cat_issues.items():
        if not cat_issue_list:
            cards.append(
                ScoreCard(
                    label=_CATEGORY_LABELS.get(cat, cat.title()),
                    score=100.0,
                    weight=weights.get(cat, 0.1),
                    grade="A",
                    issues_count=0,
                )
            )
            continue
        # Penalty-based score: deduct per severity
        penalty = sum(_severity_weight(i.severity.value) * 3 for i in cat_issue_list)
        score = max(0.0, 100.0 - penalty)
        grade = _score_to_grade(score)
        label = _CATEGORY_LABELS.get(cat, cat.title())
        cards.append(
            ScoreCard(
                label=label,
                score=score,
                weight=weights.get(cat, 0.1),
                grade=grade,
                issues_count=len(cat_issue_list),
            )
        )
    # Fill missing categories with 100/100
    for cat, weight in weights.items():
        if not any(c.label == _CATEGORY_LABELS.get(cat, cat.title()) for c in cards):
            cards.append(
                ScoreCard(
                    label=_CATEGORY_LABELS.get(cat, cat.title()),
                    score=100.0,
                    weight=weight,
                    grade="A",
                    issues_count=0,
                )
            )
    return cards


def _issue_to_row(issue: AuditIssue) -> IssueRow:
    severity = issue.severity.value if hasattr(issue.severity, "value") else issue.severity
    category = issue.category.value if hasattr(issue.category, "value") else issue.category
    return IssueRow(
        severity=severity,
        category=category,
        title=issue.title,
        url=getattr(issue, "url", None) or None,
        description=issue.description,
        recommendation=issue.recommendation,
        count=getattr(issue, "count", 1),
    )


def _build_fixes(issues: list[AuditIssue]) -> list[FixRecommendation]:
    fixes: dict[str, FixRecommendation] = {}
    for issue in issues:
        sev = issue.severity.value if hasattr(issue.severity, "value") else issue.severity
        if sev not in ("critical", "high"):
            continue
        key = issue.title
        if key not in fixes:
            priority = 1 if sev == "critical" else 2
            fixes[key] = FixRecommendation(
                priority=priority,
                title=issue.title,
                description=issue.recommendation or issue.description,
                url=getattr(issue, "url", None) or None,
                estimated_impact=f"Severity: {sev.title()}",
            )
    # Sort by priority then return
    return sorted(fixes.values(), key=lambda f: (f.priority, f.title))


def _build_findings(audit_report: AuditReport, overall: float) -> list[str]:
    findings = []
    if overall < 60:
        findings.append("Site has severe SEO issues requiring immediate attention.")
    elif overall < 80:
        findings.append("Site has moderate SEO issues that should be addressed.")
    else:
        findings.append("Site SEO is in good shape with minor improvements possible.")
    # Count by severity
    sev_counts: dict[str, int] = {}
    for issue in audit_report.issues:
        s = issue.severity.value if hasattr(issue.severity, "value") else issue.severity
        sev_counts[s] = sev_counts.get(s, 0) + 1
    critical = sev_counts.get("critical", 0)
    high = sev_counts.get("high", 0)
    if critical > 0:
        findings.append(f"{critical} critical issue(s) must be fixed immediately.")
    if high > 0:
        findings.append(f"{high} high-priority issue(s) should be fixed soon.")
    return findings


def _build_summary(audit_report: AuditReport, overall: float) -> str:
    total = len(audit_report.issues)
    if total == 0:
        return f"The SEO audit of the site found no issues. Overall score: {overall:.0f}/100."
    sev_counts: dict[str, int] = {}
    for issue in audit_report.issues:
        s = issue.severity.value if hasattr(issue.severity, "value") else issue.severity
        sev_counts[s] = sev_counts.get(s, 0) + 1
    crit = sev_counts.get("critical", 0)
    high = sev_counts.get("high", 0)
    msg = f"Audit complete with {total} issue(s) found"
    if crit:
        msg += f" ({crit} critical)"
    elif high:
        msg += f" ({high} high)"
    return msg + f". Overall SEO score: {overall:.0f}/100."
