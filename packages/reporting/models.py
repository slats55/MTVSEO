"""Report data models — format-agnostic, no database dependency."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ReportFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    PDF = "pdf"


class ReportType(str, Enum):
    TECHNICAL_SEO = "technical_seo"
    GEO_AUDIT = "geo_audit"
    CRAWL_SUMMARY = "crawl_summary"
    CONTENT_ANALYSIS = "content_analysis"
    FULL_AUDIT = "full_audit"


# ---------------------------------------------------------------------------
# Core report structures
# ---------------------------------------------------------------------------

@dataclass
class ScoreCard:
    """Individual score component with grade."""
    label: str
    score: float          # 0-100
    weight: float         # 0-1 (what fraction of total this represents)
    grade: str            # "A"-"F" computed from score
    issues_count: int = 0
    description: Optional[str] = None

    def __post_init__(self):
        if self.grade == "":
            self.grade = self._compute_grade(self.score)

    @staticmethod
    def _compute_grade(score: float) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"


@dataclass
class IssueRow:
    """A single issue row in the report's issue table."""
    severity: str          # critical / high / medium / low / info
    category: str
    title: str
    url: Optional[str] = None
    description: Optional[str] = None
    recommendation: Optional[str] = None
    count: int = 1


@dataclass
class FixRecommendation:
    """One actionable fix."""
    priority: int         # 1 = highest
    title: str
    description: str
    url: Optional[str] = None
    estimated_impact: Optional[str] = None  # e.g. "+5 SEO points"


# ---------------------------------------------------------------------------
# Report data — intermediate representation consumed by formatters
# ---------------------------------------------------------------------------

@dataclass
class ReportMetadata:
    website_url: str
    report_type: ReportType
    generated_at: str      # ISO 8601
    total_pages_crawled: int = 0
    crawl_duration_seconds: float = 0.0
    crawl_user_agent: str = "SEO-Agent-OS/1.0"
    auditor_version: str = "1.0.0"


@dataclass
class ReportData:
    """Complete report data — format-agnostic intermediate representation."""
    metadata: ReportMetadata
    overall_score: float           # 0-100
    overall_grade: str             # "A"-"F"
    score_breakdown: list[ScoreCard] = field(default_factory=list)
    issues: list[IssueRow] = field(default_factory=list)
    fixes: list[FixRecommendation] = field(default_factory=list)
    summary_text: str = ""          # 2-3 sentence executive summary
    key_findings: list[str] = field(default_factory=list)   # bullet points

    # Optional supplemental sections keyed by section name
    supplemental: dict[str, str] = field(default_factory=dict)

    def issues_by_severity(self, severity: str) -> list[IssueRow]:
        return [i for i in self.issues if i.severity == severity]

    def issues_by_category(self, category: str) -> list[IssueRow]:
        return [i for i in self.issues if i.category == category]

    def issue_counts_by_severity(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for issue in self.issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + issue.count
        return counts
