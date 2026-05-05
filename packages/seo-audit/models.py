# packages/seo-audit/models.py
"""Pydantic types for the SEO audit package.

Mirrors the SQLAlchemy SeoIssue model but uses plain Pydantic types
so the seo-audit package has no database dependency.
"""

import enum
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────


class IssueSeverity(str, enum.Enum):
    """Severity levels for SEO issues."""

    CRITICAL = "CRITICAL"   # Score impact: >15 pts — direct ranking harm
    HIGH = "HIGH"           # Score impact: 8–15 pts — significant issue
    MEDIUM = "MEDIUM"       # Score impact: 3–7 pts — moderate issue
    LOW = "LOW"             # Score impact: 1–2 pts — minor issue
    INFO = "INFO"          # Score impact: 0 — informational only


class IssueCategory(str, enum.Enum):
    """Categories of SEO issues."""

    CRAWLABILITY = "CRAWLABILITY"
    INDEXABILITY = "INDEXABILITY"
    METADATA = "METADATA"
    ARCHITECTURE = "ARCHITECTURE"
    PERFORMANCE = "PERFORMANCE"
    STRUCTURED_DATA = "STRUCTURED_DATA"
    SECURITY = "SECURITY"


# ─── Score types ──────────────────────────────────────────────────────────────


class AuditScore(BaseModel):
    """Per-category and total SEO audit score.

    Mirrors the shared SeoScoreBreakdown but with full Pydantic validation.
    Weights sum to 100.
    """

    crawlability: float = Field(ge=0, le=20, description="Crawlability score /20")
    indexability: float = Field(ge=0, le=20, description="Indexability score /20")
    metadata: float = Field(ge=0, le=15, description="Metadata/on-page score /15")
    architecture: float = Field(ge=0, le=15, description="Architecture/internal links score /15")
    performance: float = Field(ge=0, le=15, description="Performance/mobile score /15")
    structured_data: float = Field(ge=0, le=10, description="Structured data score /10")
    security: float = Field(ge=0, le=5, description="Security score /5")

    @property
    def total(self) -> float:
        return (
            self.crawlability
            + self.indexability
            + self.metadata
            + self.architecture
            + self.performance
            + self.structured_data
            + self.security
        )

    def grade(self) -> Literal["A", "B", "C", "D", "F"]:
        """Return a letter grade based on total score."""
        t = self.total
        if t >= 90:
            return "A"
        if t >= 80:
            return "B"
        if t >= 70:
            return "C"
        if t >= 60:
            return "D"
        return "F"


# ─── Issue ───────────────────────────────────────────────────────────────────


class AuditIssue(BaseModel):
    """A single SEO issue found during audit.

    Mirrors the DB SeoIssue model.
    """

    issue_type: str = Field(
        description="Machine-readable issue type, e.g. 'missing_title', 'duplicate_meta_desc'"
    )
    category: IssueCategory = Field(
        description="Which scoring category this issue belongs to"
    )
    severity: IssueSeverity
    title: str = Field(
        description="Short human-readable issue title, e.g. 'Missing title tag'"
    )
    description: str = Field(
        description="Detailed explanation of the issue and its impact"
    )
    recommendation: str = Field(
        description="Specific, actionable steps to fix the issue"
    )
    affected_element: str | None = Field(
        description="The affected URL, CSS selector, or element that has the issue"
    )
    page_url: str | None = Field(
        description="URL of the page this issue was found on"
    )
    count: int = Field(
        default=1, ge=1,
        description="How many pages are affected by this issue (for site-wide issues)"
    )

    def score_impact(self) -> float:
        """Estimated point impact on the total SEO score.

        Based on severity and category weight. Used by the scorer.
        """
        base = {
            IssueSeverity.CRITICAL: 15,
            IssueSeverity.HIGH: 10,
            IssueSeverity.MEDIUM: 5,
            IssueSeverity.LOW: 2,
            IssueSeverity.INFO: 0,
        }.get(self.severity, 0)
        return float(base)


# ─── Report ──────────────────────────────────────────────────────────────────


class AuditReport(BaseModel):
    """Full SEO audit report — produced by AuditReporter.

    Contains score breakdown, all issues, fix recommendations, and metadata.
    """

    # Identification
    domain: str
    crawl_run_id: str | None = None
    audited_at: datetime = Field(default_factory=lambda: datetime.utcnow())

    # Scores
    score: AuditScore
    total_issues: int = 0
    issues_by_severity: dict[IssueSeverity, int] = Field(default_factory=dict)
    issues_by_category: dict[IssueCategory, int] = Field(default_factory=dict)

    # Issues
    issues: list[AuditIssue] = Field(default_factory=list)

    # Counts
    pages_audited: int = 0
    pages_with_critical_issues: int = 0
    pages_with_noindex: int = 0
    duplicate_title_count: int = 0
    duplicate_meta_desc_count: int = 0

    # Recommendations (grouped by priority)
    critical_fixes: list[str] = Field(default_factory=list)
    high_priority_fixes: list[str] = Field(default_factory=list)
    medium_priority_fixes: list[str] = Field(default_factory=list)

    def issues_for_page(self, page_url: str) -> list[AuditIssue]:
        """Return all issues affecting a specific page URL."""
        return [i for i in self.issues if i.page_url == page_url]

    def summary(self) -> str:
        """One-line summary for logging / display."""
        return (
            f"SEO Audit: {self.domain} | "
            f"Score: {self.score.total:.0f}/100 ({self.score.grade()}) | "
            f"Issues: {self.total_issues} "
            f"(CRITICAL={self.issues_by_severity.get(IssueSeverity.CRITICAL, 0)}, "
            f"HIGH={self.issues_by_severity.get(IssueSeverity.HIGH, 0)}, "
            f"MEDIUM={self.issues_by_severity.get(IssueSeverity.MEDIUM, 0)})"
        )
