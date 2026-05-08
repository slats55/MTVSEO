# Keyword model.

import uuid
from sqlalchemy import Enum, Float, ForeignKey, Integer, String, UUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import KeywordIntent

class Keyword(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "keywords"

    website_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("websites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    keyword: Mapped[str] = mapped_column(String(500), nullable=False)
    intent: Mapped[KeywordIntent | None] = mapped_column(Enum(KeywordIntent))
    volume: Mapped[int | None] = mapped_column(Integer)
    difficulty: Mapped[float | None] = mapped_column(Float)
    current_rank: Mapped[int | None] = mapped_column(Integer)
    target_url: Mapped[str | None] = mapped_column(String(2000))

    # Relationships
    website = relationship("Website", back_populates="keywords")
    content_briefs = relationship("ContentBrief", back_populates="keyword")

