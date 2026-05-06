"""Markdown formatter for audit reports."""

from ...reporting.models import (
    ReportData,
    ReportMetadata,
    ScoreCard,
    IssueRow,
    FixRecommendation,
    ReportFormat,
)


class MarkdownFormatter:
    """Renders ReportData as a Markdown string."""

    def render(self, report: ReportData) -> str:
        parts = [
            self._render_header(report.metadata),
            self._render_score_summary(report),
            self._render_executive_summary(report),
            self._render_key_findings(report),
            self._render_issue_table(report),
            self._render_fixes(report),
            self._render_supplemental(report),
            self._render_footer(report.metadata),
        ]
        return "\n".join(part for part in parts if part)

    # ---------------------------------------------------------------------------
    # Section renderers
    # ---------------------------------------------------------------------------

    def _render_header(self, meta: ReportMetadata) -> str:
        type_label = meta.report_type.value.replace("_", " ").title()
        duration = f"{meta.crawl_duration_seconds:.1f}"
        return (
            f"# {type_label} Report\n"
            f"**Website:** {meta.website_url}\n"
            f"**Crawled:** {meta.generated_at}\n"
            f"**Pages crawled:** {meta.total_pages_crawled}\n"
            f"**Duration:** {duration}s\n"
            f"**Auditor:** SEO Agent OS v{meta.auditor_version}\n"
        )

    def _render_score_summary(self, report: ReportData) -> str:
        grade_badge = self._grade_badge(report.overall_grade)
        score_str = f"{report.overall_score:.0f}"
        lines = [
            "## Overall Score",
            "",
            f"# {score_str}/100 {grade_badge}",
            "",
            "| Category | Score | Grade | Issues |",
            "|:---------|------:|------:|-------:|",
        ]
        for sc in report.score_breakdown:
            badge = self._grade_badge(sc.grade)
            sc_score = f"{sc.score:.0f}"
            lines.append(
                f"| {sc.label} | {sc_score}/100 | {badge} | {sc.issues_count} |"
            )
        lines.append("")
        return "\n".join(lines)

    def _render_executive_summary(self, report: ReportData) -> str:
        if not report.summary_text:
            return ""
        return "## Executive Summary\n\n" + report.summary_text + "\n\n"

    def _render_key_findings(self, report: ReportData) -> str:
        if not report.key_findings:
            return ""
        lines = ["## Key Findings", ""]
        for finding in report.key_findings:
            lines.append(f"- {finding}")
        lines.append("")
        return "\n".join(lines)

    def _render_issue_table(self, report: ReportData) -> str:
        if not report.issues:
            return "## Issues Found\n\n*No critical or high issues found.*\n"

        # Group by severity
        severity_order = ["critical", "high", "medium", "low", "info"]
        lines = ["## Issues", "", self._issue_table_header()]

        for severity in severity_order:
            for issue in report.issues:
                if issue.severity == severity:
                    lines.append(self._issue_row(issue))

        lines.append("")
        return "\n".join(lines)

    def _issue_table_header(self) -> str:
        return (
            "| # | Severity | Category | Issue | Location | Recommendation |\n"
            "|---|:---------|:---------|:------|:---------|:---------------|"
        )

    def _issue_row(self, issue: IssueRow) -> str:
        severity_icon = self._severity_icon(issue.severity)
        location = issue.url or "\u2014"  # em-dash
        rec = issue.recommendation or "\u2014"
        # Truncate long titles
        title = (issue.title[:80] + "...") if len(issue.title) > 80 else issue.title
        return (
            f"| {severity_icon} | **{issue.severity.upper()}** | "
            f"{issue.category} | {title} | {location} | {rec} |"
        )

    def _render_fixes(self, report: ReportData) -> str:
        if not report.fixes:
            return ""
        lines = [
            "## Priority Fixes",
            "",
            "| Priority | Action | Impact |",
            "|:--------:|:-------|:------:|",
        ]
        for fix in sorted(report.fixes, key=lambda f: f.priority):
            impact = fix.estimated_impact or "\u2014"
            lines.append(
                f"| {fix.priority} | **{fix.title}**<br>{fix.description} | {impact} |"
            )
        lines.append("")
        return "\n".join(lines)

    def _render_supplemental(self, report: ReportData) -> str:
        if not report.supplemental:
            return ""
        lines = ["## Supplemental Data", ""]
        for title, content in report.supplemental.items():
            lines.append(f"### {title}")
            lines.append(content)
            lines.append("")
        return "\n".join(lines)

    def _render_footer(self, meta: ReportMetadata) -> str:
        return (
            "---\n\n"
            f"*Report generated by SEO Agent OS \u2014 {meta.generated_at}*\n"
        )

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    @staticmethod
    def _grade_badge(grade: str) -> str:
        color_map = {
            "A": "\U0001f7e2",  # green circle
            "B": "\U0001f7e1",  # yellow circle
            "C": "\U0001f7e0",  # orange circle
            "D": "\U0001f534",  # red circle
            "F": "\U0001f6ab",  # red no entry
        }
        return color_map.get(grade, "")

    @staticmethod
    def _severity_icon(severity: str) -> str:
        icons = {
            "critical": "\U0001f534",  # red circle
            "high": "\U0001f7e0",      # orange circle
            "medium": "\U0001f7e1",     # yellow circle
            "low": "\U0001f535",        # blue circle
            "info": "\u26aa",           # white circle
        }
        return icons.get(severity, "\u26aa")
