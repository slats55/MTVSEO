# SchemaDraft model.

import uuid
from sqlalchemy import Boolean, Enum, ForeignKey, JSON, String, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import SchemaStatus

class SchemaDraft(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "schema_drafts"

    website_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("websites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page_url: Mapped[str | None] = mapped_column(String(2000))
    schema_type: Mapped[str | None] = mapped_column(String(100))
    schema_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    validation_errors: Mapped[dict | None] = mapped_column(JSON, default=dict)
    status: Mapped[SchemaStatus] = mapped_column(
        Enum(SchemaStatus), default=SchemaStatus.DRAFT, nullable=False
    )

    # Relationships
    website = relationship("Website", back_populates="schema_drafts")

