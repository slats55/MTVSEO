# Website model.

import uuid
from sqlalchemy import ForeignKey, String, UUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Website(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "websites"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    business = relationship("Business", back_populates="websites")
    crawl_runs = relationship("CrawlRun", back_populates="website", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="website", cascade="all, delete-orphan")
    topic_clusters = relationship("TopicCluster", back_populates="website", cascade="all, delete-orphan")
    schema_drafts = relationship("SchemaDraft", back_populates="website", cascade="all, delete-orphan")
    internal_link_opportunities = relationship(
        "InternalLinkOpportunity",
        back_populates="website",
        cascade="all, delete-orphan",
    )

