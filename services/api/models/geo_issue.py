# GeoIssue model.

import uuid
from sqlalchemy import Enum, Float, ForeignKey, String, Text, UUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import IssueSeverity

class GeoIssue(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "geo_issues"

    page_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crawl_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crawl_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    issue_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[IssueSeverity] = mapped_column(Enum(IssueSeverity), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    recommendation: Mapped[str | None] = mapped_column(Text)
    score_impact: Mapped[float | None] = mapped_column(Float, default=0.0)

    # Relationships
    page = relationship("Page", back_populates="geo_issues")
    crawl_run = relationship("CrawlRun", back_populates="geo_issues")

