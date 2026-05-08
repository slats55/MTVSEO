# TopicCluster model.

import uuid
from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class TopicCluster(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "topic_clusters"

    website_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("websites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    pillar_page_url: Mapped[str | None] = mapped_column(String(2000))
    search_volume: Mapped[int | None] = mapped_column(Integer)
    priority: Mapped[int | None] = mapped_column(Integer)

    # Relationships
    website = relationship("Website", back_populates="topic_clusters")

