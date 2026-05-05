# Pydantic models for the crawler package.
# These types are independent from the SQLAlchemy DB models, but mirror their fields.
# Used for internal crawl pipeline and worker output — NOT imported by services/api.

from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, HttpUrl, field_validator


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _extract_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or parsed.path


# ─── Config ──────────────────────────────────────────────────────────────────


class CrawlConfig(BaseModel):
    """Configuration for a single crawl run."""

    start_url: HttpUrl
    domain: str | None = None
    max_pages: int = Field(default=50, ge=1, le=500)
    crawl_depth: int = Field(default=3, ge=0, le=10)
    respect_robots: bool = True
    delay_ms: int = Field(default=500, ge=0, le=30_000)
    user_agent: str = "SEO-Agent-OS/1.0 (+https://github.com/seo-agent-os)"
    timeout_ms: int = Field(default=15_000, ge=1_000, le=60_000)
    obey_crawl_delay: bool = True  # honor Crawl-delay in robots.txt

    # Internal crawl options
    follow_sitemaps: bool = True
    max_redirects: int = 5

    def __init__(self, **data: Any) -> None:
        # Auto-extract domain from start_url if not provided
        if "start_url" in data and "domain" not in data:
            data["domain"] = _extract_domain(str(data["start_url"]))
        super().__init__(**data)

    @field_validator("start_url", mode="before")
    @classmethod
    def _ensure_scheme(cls, v: str) -> str:
        if isinstance(v, str) and not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v

    @property
    def delay_seconds(self) -> float:
        return self.delay_ms / 1000.0


# ─── Page record ─────────────────────────────────────────────────────────────


class PageRecord(BaseModel):
    """Normalized representation of a single crawled page.
    
    Mirrors the SQLAlchemy Page model but uses plain Pydantic types
    so the crawler package has no database dependency.
    """

    url: str
    canonical_url: str | None = None
    status_code: int | None = None
    title: str | None = None
    meta_description: str | None = None
    h1: str | None = None
    h2_headings: list[str] = Field(default_factory=list)
    word_count: int | None = None
    internal_links_count: int = 0
    external_links_count: int = 0
    images_count: int = 0
    images_without_alt: int = 0
    has_schema: bool = False
    schema_types: list[str] = Field(default_factory=list)
    is_indexable: bool = True
    is_canonical: bool = True
    is_robots_blocked: bool = False
    crawl_depth: int = 0
    parent_page_url: str | None = None
    redirect_url: str | None = None
    raw_html: str | None = None
    fetched_at: datetime | None = None

    # Discovered links (transient — not stored in DB, used for crawl frontier)
    outbound_urls: list[str] = Field(default_factory=list)


# ─── Crawl result ─────────────────────────────────────────────────────────────


class CrawlResult(BaseModel):
    """Full result of a crawl run — returned by CrawlRunner.run()."""

    config: CrawlConfig
    started_at: datetime
    completed_at: datetime | None = None
    pages_discovered: int = 0
    pages_crawled: int = 0
    pages: list[PageRecord] = Field(default_factory=list)
    error_message: str | None = None

    @property
    def duration_seconds(self) -> float | None:
        if self.completed_at is None:
            return None
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def success(self) -> bool:
        return self.error_message is None and self.pages_crawled > 0


# ─── Summary ──────────────────────────────────────────────────────────────────


class CrawlSummary(BaseModel):
    """High-level summary of a crawl run, suitable for storage in CrawlRun."""

    pages_discovered: int = 0
    pages_crawled: int = 0
    crawl_duration_seconds: float | None = None
    error_count: int = 0
    blocked_by_robots_count: int = 0
    non_indexable_count: int = 0
    pages_with_schema_count: int = 0
    average_word_count: float | None = None
