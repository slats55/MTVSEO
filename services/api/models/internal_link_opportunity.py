# InternalLinkOpportunity model.

import uuid
from sqlalchemy import Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import LinkType

class InternalLinkOpportunity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "internal_link_opportunities"

    website_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("websites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_page_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("pages.id"), nullable=False
    )
    target_page_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("pages.id"), nullable=False
    )
    suggested_anchor_text: Mapped[str | None] = mapped_column(String(500))
    link_type: Mapped[LinkType] = mapped_column(
        Enum(LinkType), default=LinkType.INTERNAL, nullable=False
    )
    priority: Mapped[int | None] = mapped_column(Integer)

    # Relationships
    website = relationship("Website", back_populates="internal_link_opportunities")

