# ContentDraft model.

import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import DraftStatus

class ContentDraft(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "content_drafts"

    content_brief_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String(500))
    slug: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str | None] = mapped_column(Text)
    content_html: Mapped[str | None] = mapped_column(Text)
    meta_title: Mapped[str | None] = mapped_column(String(500))
    meta_description: Mapped[str | None] = mapped_column(String(1000))
    word_count: Mapped[int | None] = mapped_column(Integer)
    schema_markup: Mapped[dict | None] = mapped_column(JSON, default=dict)
    internal_links: Mapped[dict | None] = mapped_column(JSON, default=dict)
    compliance_flags: Mapped[dict | None] = mapped_column(JSON, default=dict)
    compliance_notes: Mapped[dict | None] = mapped_column(JSON, default=dict)
    usefulness_score: Mapped[float | None] = mapped_column(Float)
    status: Mapped[DraftStatus] = mapped_column(
        Enum(DraftStatus), default=DraftStatus.DRAFT, nullable=False
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    brief = relationship("ContentBrief", back_populates="drafts")
    publishing_jobs = relationship("PublishingJob", back_populates="draft")

