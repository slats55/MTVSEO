# Page model.

import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Page(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "pages"

    crawl_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crawl_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    canonical_url: Mapped[str | None] = mapped_column(String(2000))
    status_code: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(500))
    meta_description: Mapped[str | None] = mapped_column(String(1000))
    h1: Mapped[str | None] = mapped_column(String(500))
    h2_headings: Mapped[list | None] = mapped_column(JSON, default=list)
    word_count: Mapped[int | None] = mapped_column(Integer)
    internal_links_count: Mapped[int] = mapped_column(Integer, default=0)
    external_links_count: Mapped[int] = mapped_column(Integer, default=0)
    images_count: Mapped[int] = mapped_column(Integer, default=0)
    images_without_alt: Mapped[int] = mapped_column(Integer, default=0)
    has_schema: Mapped[bool] = mapped_column(Boolean, default=False)
    schema_types: Mapped[list | None] = mapped_column(JSON, default=list)
    is_indexable: Mapped[bool] = mapped_column(Boolean, default=True)
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=True)
    is_robots_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    crawl_depth: Mapped[int | None] = mapped_column(Integer)
    parent_page_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pages.id")
    )
    redirect_url: Mapped[str | None] = mapped_column(String(2000))

    # Relationships
    crawl_run = relationship("CrawlRun", back_populates="pages")
    snapshot = relationship("PageSnapshot", back_populates="page", uselist=False, cascade="all, delete-orphan")
    seo_issues = relationship("SeoIssue", back_populates="page", cascade="all, delete-orphan")
    geo_issues = relationship("GeoIssue", back_populates="page", cascade="all, delete-orphan")

