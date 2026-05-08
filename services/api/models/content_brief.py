# ContentBrief model.

import uuid
from sqlalchemy import Enum, ForeignKey, Integer, JSON, String, UUID
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import BriefStatus, KeywordIntent

class ContentBrief(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "content_briefs"

    website_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("websites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    keyword_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("keywords.id")
    )
    title: Mapped[str | None] = mapped_column(String(500))
    target_url: Mapped[str | None] = mapped_column(String(2000))
    intent: Mapped[KeywordIntent | None] = mapped_column(Enum(KeywordIntent))
    word_count_target: Mapped[int | None] = mapped_column(Integer)
    key_questions: Mapped[list | None] = mapped_column(JSON, default=list)
    key_points: Mapped[list | None] = mapped_column(JSON, default=list)
    competitor_urls: Mapped[list | None] = mapped_column(JSON, default=list)
    recommended_schema: Mapped[dict | None] = mapped_column(JSON, default=dict)
    internal_link_targets: Mapped[dict | None] = mapped_column(JSON, default=dict)
    compliance_flags: Mapped[dict | None] = mapped_column(JSON, default=dict)
    status: Mapped[BriefStatus] = mapped_column(
        Enum(BriefStatus), default=BriefStatus.DRAFT, nullable=False
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # Relationships
    website = relationship("Website")
    keyword = relationship("Keyword", back_populates="content_briefs")
    drafts = relationship("ContentDraft", back_populates="brief", cascade="all, delete-orphan")

