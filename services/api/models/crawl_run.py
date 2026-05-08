# CrawlRun model.

import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import CrawlStatus

class CrawlRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "crawl_runs"

    website_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("websites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[CrawlStatus] = mapped_column(
        Enum(CrawlStatus), default=CrawlStatus.PENDING, nullable=False
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

