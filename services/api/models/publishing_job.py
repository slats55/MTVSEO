# PublishingJob model.

import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, UUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import PublishDestination, PublishStatus

class PublishingJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "publishing_jobs"

    content_draft_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    destination: Mapped[PublishDestination] = mapped_column(
        Enum(PublishDestination), nullable=False
    )
    destination_url: Mapped[str | None] = mapped_column(String(2000))
    status: Mapped[PublishStatus] = mapped_column(
        Enum(PublishStatus), default=PublishStatus.PENDING_REVIEW, nullable=False
    )
    submitted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    published_url: Mapped[str | None] = mapped_column(String(2000))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    draft = relationship("ContentDraft", back_populates="publishing_jobs")

