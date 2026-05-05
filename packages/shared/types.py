# Shared type aliases and simple dataclasses.
# No internal dependencies — safe to import from any package.

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, TypedDict
from uuid import UUID


# ─── Score types ───────────────────────────────────────────────────────────────


@dataclass
class SeoScoreBreakdown:
    crawlability: float      # /20
    indexability: float     # /20
    metadata: float         # /15
    architecture: float      # /15
    performance: float      # /15
    structured_data: float  # /10
    security: float         # /5
    total: float            # /100


@dataclass
class GeoScoreBreakdown:
    ai_crawler_access: float       # /15
    entity_clarity: float         # /15
    citability: float             # /25
    content_depth: float          # /20
    schema: float                # /10
    brand_authority: float       # /10
    llms_readability: float      # /5
    total: float                  # /100


@dataclass
class ContentOpportunityScore:
    business_value: float         # /25
    search_intent: float          # /20
    ranking_gap: float            # /15
    conversion_likelihood: float  # /20
    content_feasibility: float    # /10
    internal_link_support: float  # /10
    total: float                  # /100


# ─── Crawl types ───────────────────────────────────────────────────────────────


class CrawlConfigDict(TypedDict, total=False):
    start_url: str
    max_pages: int
    crawl_depth: int
    respect_robots: bool
    delay_ms: int
    user_agent: str
    timeout_ms: int


# ─── Audit result types ───────────────────────────────────────────────────────


class SeoIssueDict(TypedDict):
    issue_type: str
    severity: str
    title: str
    description: str
    recommendation: str
    affected_element: str | None


class GeoIssueDict(TypedDict):
    issue_type: str
    severity: str
    title: str
    description: str
    recommendation: str
    score_impact: float


class AuditResultDict(TypedDict):
    seo_score: float
    seo_breakdown: dict
    seo_issues: list[SeoIssueDict]
    geo_score: float
    geo_breakdown: dict
    geo_issues: list[GeoIssueDict]


# ─── Content types ─────────────────────────────────────────────────────────────


class ComplianceFlagDict(TypedDict):
    is_cannabis: bool
    is_ymyl: bool
    passed: bool
    failed_checks: list[str]


# ─── URL / text helpers return types ─────────────────────────────────────────


@dataclass
class ParsedUrl:
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str
    canonical: str  # Normalized, stripped trailing slash


@dataclass
class ReadingTime:
    minutes: float
    word_count: int
    label: str  # e.g. "3 min read"


# ─── Storage path builder result ──────────────────────────────────────────────


@dataclass
class StoragePaths:
    reports_dir: str
    exports_dir: str
    snapshots_dir: str
    schema_outputs_dir: str
    report_path: str      # (business_id, run_id) -> full path
    snapshot_path: str    # (page_id, run_id) -> full path
