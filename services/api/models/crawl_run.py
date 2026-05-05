# CrawlRun model.

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import CrawlStatus


class CrawlRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "crawl_runs"

    website_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    status: Mapped[CrawlStatus] = mapped_column(
        CrawlStatus, default=CrawlStatus.PENDING, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pages_discovered: Mapped[int] = mapped_column(Integer, default=0)
    pages_crawled: Mapped[int] = mapped_column(Integer, default=0)
    crawl_depth: Mapped[int] = mapped_column(Integer, default=3)
    max_pages: Mapped[int] = mapped_column(Integer, default=50)
    error_message: Mapped[str | None] = mapped_column(Text)

    # Relationships
    website = relationship("Website", back_populates="crawl_runs")
    pages = relationship("Page", back_populates="crawl_run", cascade="all, delete-orphan")
    seo_issues = relationship("SeoIssue", back_populates="crawl_run", cascade="all, delete-orphan")
    geo_issues = relationship("GeoIssue", back_populates="crawl_run", cascade="all, delete-orphan")


import uuid
from datetime import datetime
