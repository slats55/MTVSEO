"""Content analysis report generator.

Produces a content quality report from crawled pages (PageRecord list).
No DB dependency, no audit — pure content analysis.
"""

from datetime import datetime, timezone
from ...crawler.models import PageRecord, CrawlResult
from ...models import (
    ReportData,
    ReportMetadata,
    ReportType,
    ScoreCard,
    IssueRow,
    FixRecommendation,
)


# Ideal ranges
_TITLE_LEN_MIN, _TITLE_LEN_MAX = 30, 60
_DESC_LEN_MIN, _DESC_LEN_MAX = 70, 160
_H1_LEN_MAX = 60
_MIN_WORD_COUNT = 300
_MAX_FETCH_TIME_MS = 2000


class ContentReportGenerator:
    """Analyzes crawled pages for content quality issues."""

    def run(
        self,
        pages: list[PageRecord],
        website_url: str,
    ) -> ReportData:
        """Build a ReportData from a list of PageRecords."""
        meta = ReportMetadata(
            website_url=website_url,
            report_type=ReportType.CONTENT_ANALYSIS,
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_pages_crawled=len(pages),
            crawl_duration_seconds=0.0,
        )

        score_breakdown = self._score_breakdown(pages)
        overall = self._overall_score(score_breakdown)
        overall_grade = self._score_to_grade(overall)
        issues = self._collect_issues(pages)
        fixes = self._collect_fixes(issues)
        key_findings = self._build_findings(pages, issues)
        summary_text = self._build_summary(pages, issues)

        return ReportData(
            metadata=meta,
            overall_score=overall,
            overall_grade=overall_grade,
            score_breakdown=score_breakdown,
            issues=issues,
            fixes=fixes,
            summary_text=summary_text,
            key_findings=key_findings,
            supplemental=self._build_supplemental(pages),
        )

    # ---------------------------------------------------------------------------
    # Score breakdown
    # ---------------------------------------------------------------------------

    def _score_breakdown(self, pages: list[PageRecord]) -> list[ScoreCard]:
        if not pages:
            return [
                ScoreCard("Titles", 0.0, 0.20, "F", 0),
                ScoreCard("Meta Descriptions", 0.0, 0.15, "F", 0),
                ScoreCard("Headings", 0.0, 0.15, "F", 0),
                ScoreCard("Content Quality", 0.0, 0.25, "F", 0),
                ScoreCard("Image Optimization", 0.0, 0.15, "F", 0),
                ScoreCard("Readability", 0.0, 0.10, "F", 0),
            ]

        # Title score
        title_ok = sum(1 for p in pages if p.title and _TITLE_LEN_MIN <= len(p.title) <= _TITLE_LEN_MAX)
        title_score = (title_ok / len(pages)) * 100
        title_issues = len(pages) - title_ok

        # Meta description score
        desc_ok = sum(1 for p in pages if p.meta_description and _DESC_LEN_MIN <= len(p.meta_description) <= _DESC_LEN_MAX)
        desc_score = (desc_ok / len(pages)) * 100
        desc_issues = len(pages) - desc_ok

        # Headings score (has H1, H1 length OK)
        h1_ok = sum(1 for p in pages if p.h1 and len(p.h1) <= _H1_LEN_MAX)
        h1_score = (h1_ok / len(pages)) * 100
        h1_issues = len(pages) - h1_ok

        # Content quality (word count)
        content_ok = sum(1 for p in pages if (p.word_count or 0) >= _MIN_WORD_COUNT)
        content_score = (content_ok / len(pages)) * 100
        content_issues = len(pages) - content_ok

        # Image optimization (has images, all have alt)
        pages_with_images = [p for p in pages if p.images and len(p.images) > 0]
        if pages_with_images:
            img_ok = sum(1 for p in pages_with_images if all(a for a in (img.alt or "" for img in p.images)))
            img_score = (img_ok / len(pages_with_images)) * 100
            img_issues = len(pages_with_images) - img_ok
        else:
            img_score = 100.0
            img_issues = 0

        # Readability (avg word count as proxy — no Flesch score without text analysis)
        avg_words = sum(p.word_count or 0 for p in pages) / len(pages)
        readability_score = min(100.0, (avg_words / 800) * 100)

        return [
            ScoreCard("Titles", title_score, 0.20, self._score_to_grade(title_score), title_issues),
            ScoreCard("Meta Descriptions", desc_score, 0.15, self._score_to_grade(desc_score), desc_issues),
            ScoreCard("Headings", h1_score, 0.15, self._score_to_grade(h1_score), h1_issues),
            ScoreCard("Content Quality", content_score, 0.25, self._score_to_grade(content_score), content_issues),
            ScoreCard("Image Optimization", img_score, 0.15, self._score_to_grade(img_score), img_issues),
            ScoreCard("Readability", readability_score, 0.10, self._score_to_grade(readability_score), 0),
        ]

    def _overall_score(self, breakdown: list[ScoreCard]) -> float:
        return sum(s.score * s.weight for s in breakdown)

    @staticmethod
    def _score_to_grade(score: float) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"

    # ---------------------------------------------------------------------------
    # Issue collection
    # ---------------------------------------------------------------------------

    def _collect_issues(self, pages: list[PageRecord]) -> list[IssueRow]:
        issues = []
        for page in pages:
            # Title issues
            if not page.title:
                issues.append(
                    IssueRow(
                        severity="high",
                        category="Titles",
                        title="Missing page title",
                        url=page.url,
                        description="Page has no <title> tag.",
                        recommendation="Add a unique <title> tag between 30-60 characters.",
                    )
                )
            elif len(page.title) > _TITLE_LEN_MAX:
                issues.append(
                    IssueRow(
                        severity="medium",
                        category="Titles",
                        title="Title tag too long",
                        url=page.url,
                        description=f"Title is {len(page.title)} characters (max recommended: {_TITLE_LEN_MAX}).",
                        recommendation=f"Shorten title to under {_TITLE_LEN_MAX} characters.",
                    )
                )
            elif len(page.title) < _TITLE_LEN_MIN:
                issues.append(
                    IssueRow(
                        severity="low",
                        category="Titles",
                        title="Title tag too short",
                        url=page.url,
                        description=f"Title is only {len(page.title)} characters (min recommended: {_TITLE_LEN_MIN}).",
                        recommendation=f"Expand title to at least {_TITLE_LEN_MIN} characters.",
                    )
                )

            # Meta description issues
            if not page.meta_description:
                issues.append(
                    IssueRow(
                        severity="medium",
                        category="Meta Descriptions",
                        title="Missing meta description",
                        url=page.url,
                        description="Page has no meta description.",
                        recommendation="Add a meta description of 120-160 characters.",
                    )
                )
            elif len(page.meta_description) > _DESC_LEN_MAX:
                issues.append(
                    IssueRow(
                        severity="low",
                        category="Meta Descriptions",
                        title="Meta description too long",
                        url=page.url,
                        description=f"Meta description is {len(page.meta_description)} characters.",
                        recommendation=f"Shorten to under {_DESC_LEN_MAX} characters.",
                    )
                )

            # H1 issues
            if not page.h1:
                issues.append(
                    IssueRow(
                        severity="medium",
                        category="Headings",
                        title="Missing H1 heading",
                        url=page.url,
                        description="Page has no H1 heading.",
                        recommendation="Add a single H1 heading that matches or closely matches the page title.",
                    )
                )
            elif len(page.h1) > _H1_LEN_MAX:
                issues.append(
                    IssueRow(
                        severity="low",
                        category="Headings",
                        title="H1 heading too long",
                        url=page.url,
                        description=f"H1 is {len(page.h1)} characters (max: {_H1_LEN_MAX}).",
                        recommendation=f"Shorten H1 to under {_H1_LEN_MAX} characters.",
                    )
                )

            # Thin content
            wc = page.word_count or 0
            if wc < 100:
                issues.append(
                    IssueRow(
                        severity="high",
                        category="Content Quality",
                        title="Very thin content",
                        url=page.url,
                        description=f"Page has only {wc} words. This is likely a thin doorway page.",
                        recommendation="Expand content to at least 300 words or consider removing the page.",
                    )
                )
            elif wc < _MIN_WORD_COUNT:
                issues.append(
                    IssueRow(
                        severity="medium",
                        category="Content Quality",
                        title="Thin content",
                        url=page.url,
                        description=f"Page has only {wc} words (minimum recommended: {_MIN_WORD_COUNT}).",
                        recommendation=f"Expand content to at least {_MIN_WORD_COUNT} words for better SEO.",
                    )
                )

            # Image alt issues
            if page.images:
                for img in page.images:
                    if not img.alt or img.alt.strip() in ("", "image", "photo", "pic"):
                        issues.append(
                            IssueRow(
                                severity="low",
                                category="Image Optimization",
                                title="Image missing descriptive alt text",
                                url=page.url,
                                description=f"Image '{img.src}' has missing or generic alt text.",
                                recommendation="Add descriptive alt text that includes relevant keywords where appropriate.",
                            )
                        )

        return issues

    def _collect_fixes(self, issues: list[IssueRow]) -> list[FixRecommendation]:
        fixes: dict[str, FixRecommendation] = {}
        for issue in issues:
            if issue.severity not in ("critical", "high", "medium"):
                continue
            if issue.title in fixes:
                continue
            priority_map = {"critical": 1, "high": 2, "medium": 3}
            fixes[issue.title] = FixRecommendation(
                priority=priority_map.get(issue.severity, 4),
                title=issue.title,
                description=issue.recommendation or issue.description,
                url=issue.url,
            )
        return sorted(fixes.values(), key=lambda f: (f.priority, f.title))

    # ---------------------------------------------------------------------------
    # Findings / summary helpers
    # ---------------------------------------------------------------------------

    def _build_findings(self, pages: list[PageRecord], issues: list[IssueRow]) -> list[str]:
        findings = []
        if not pages:
            findings.append("No pages were crawled.")
            return findings
        no_title = sum(1 for p in pages if not p.title)
        if no_title:
            findings.append(f"{no_title} page(s) are missing title tags.")
        no_desc = sum(1 for p in pages if not p.meta_description)
        if no_desc:
            findings.append(f"{no_desc} page(s) are missing meta descriptions.")
        thin = sum(1 for p in pages if (p.word_count or 0) < _MIN_WORD_COUNT)
        if thin:
            findings.append(f"{thin} page(s) have thin content below {_MIN_WORD_COUNT} words.")
        return findings

    def _build_summary(self, pages: list[PageRecord], issues: list[IssueRow]) -> str:
        total = len(pages)
        if total == 0:
            return "No pages were crawled for content analysis."
        high_issues = sum(1 for i in issues if i.severity in ("critical", "high"))
        medium_issues = sum(1 for i in issues if i.severity == "medium")
        avg_words = int(sum(p.word_count or 0 for p in pages) / total) if total else 0
        return (
            f"Content analysis of {total} page(s) found {high_issues} high-priority issue(s), "
            f"{medium_issues} medium-priority issue(s). "
            f"Average word count: {avg_words} words/page."
        )

    def _build_supplemental(self, pages: list[PageRecord]) -> dict[str, str]:
        if not pages:
            return {}

        # Top pages by word count
        top = sorted(pages, key=lambda p: p.word_count or 0, reverse=True)[:10]
        top_lines = ["| URL | Word Count |", "|:-----|------------:|"]
        for p in top:
            top_lines.append(f"| {p.url} | {p.word_count or 0} |")

        # Pages missing key elements
        missing = [p for p in pages if not p.title or not p.meta_description or not p.h1]
        missing_lines = ["| URL | Missing |", "|:-----|:--------|"]
        for p in missing:
            missing_parts = []
            if not p.title: missing_parts.append("Title")
            if not p.meta_description: missing_parts.append("Meta Desc")
            if not p.h1: missing_parts.append("H1")
            missing_lines.append(f"| {p.url} | {', '.join(missing_parts)} |")

        return {
            "Top 10 Pages by Word Count": "\n".join(top_lines),
            "Pages Missing Key Elements": "\n".join(missing_lines),
        }
