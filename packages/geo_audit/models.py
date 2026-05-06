# packages/geo-audit/models.py
"""Pydantic types for the GEO / AI visibility audit package.

Mirrors the SQLAlchemy GeoIssue model with plain Pydantic types
so this package has no database dependency.
"""

import enum
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────


class GeoIssueSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class GeoIssueCategory(str, enum.Enum):
    AI_CRAWLER_ACCESS = "AI_CRAWLER_ACCESS"
    CITABILITY = "CITABILITY"
    ENTITY_OPTIMIZATION = "ENTITY_OPTIMIZATION"
    AI_ANSWER_READINESS = "AI_ANSWER_READINESS"
    LLM_OUTPUT_OPTIMIZATION = "LLM_OUTPUT_OPTIMIZATION"


# ─── Score types ──────────────────────────────────────────────────────────────


class GeoScore(BaseModel):
    """Per-category and total GEO / AI visibility score.

    Weights sum to 100:
      AI Crawler Access:        15
      Entity Clarity:           15
      Citability:               25
      Content Depth:            20
      Schema / Structured Data: 10
      Brand Authority Signals:   10
      LLM Output Optimization:  5
    """

    ai_crawler_access: float = Field(ge=0, le=15)
    entity_clarity: float = Field(ge=0, le=15)
    citability: float = Field(ge=0, le=25)
    content_depth: float = Field(ge=0, le=20)
    schema: float = Field(ge=0, le=10)
    brand_authority: float = Field(ge=0, le=10)
    llm_readability: float = Field(ge=0, le=5)

    @property
    def total(self) -> float:
        return (
            self.ai_crawler_access
            + self.entity_clarity
            + self.citability
            + self.content_depth
            + self.schema
            + self.brand_authority
            + self.llm_readability
        )

    def grade(self) -> Literal["A", "B", "C", "D", "F"]:
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


class GeoIssue(BaseModel):
    """A single GEO / AI visibility issue found during audit."""

    issue_type: str
    category: GeoIssueCategory
    severity: GeoIssueSeverity
    title: str
    description: str
    recommendation: str
    affected_element: str | None = None
    page_url: str | None = None
    count: int = Field(default=1, ge=1)

    def score_impact(self) -> float:
        base = {
            GeoIssueSeverity.CRITICAL: 15,
            GeoIssueSeverity.HIGH: 10,
            GeoIssueSeverity.MEDIUM: 5,
            GeoIssueSeverity.LOW: 2,
            GeoIssueSeverity.INFO: 0,
        }.get(self.severity, 0)
        return float(base)


# ─── Report ──────────────────────────────────────────────────────────────────


class GeoAuditReport(BaseModel):
    """Full GEO / AI visibility audit report."""

    domain: str
    crawl_run_id: str | None = None
    audited_at: datetime = Field(default_factory=lambda: datetime.utcnow())

    score: GeoScore
    total_issues: int = 0
    issues_by_severity: dict[GeoIssueSeverity, int] = Field(default_factory=dict)
    issues_by_category: dict[GeoIssueCategory, int] = Field(default_factory=dict)

    issues: list[GeoIssue] = Field(default_factory=list)

    pages_audited: int = 0
    llms_txt_found: bool = False
    homepage_has_organization_schema: bool = False
    pages_with_entity_signals: int = 0
    pages_with_proof_signals: int = 0

    # Recommendations grouped by priority
    critical_fixes: list[str] = Field(default_factory=list)
    high_priority_fixes: list[str] = Field(default_factory=list)
    medium_priority_fixes: list[str] = Field(default_factory=list)

    # Draft llms.txt content if missing
    llms_txt_draft: str | None = None

    def issues_for_page(self, page_url: str) -> list[GeoIssue]:
        return [i for i in self.issues if i.page_url == page_url]

    def summary(self) -> str:
        return (
            f"GEO Audit: {self.domain} | "
            f"Score: {self.score.total:.0f}/100 ({self.score.grade()}) | "
            f"Issues: {self.total_issues} "
            f"(CRITICAL={self.issues_by_severity.get(GeoIssueSeverity.CRITICAL, 0)}, "
            f"HIGH={self.issues_by_severity.get(GeoIssueSeverity.HIGH, 0)}, "
            f"MEDIUM={self.issues_by_severity.get(GeoIssueSeverity.MEDIUM, 0)})"
        )
