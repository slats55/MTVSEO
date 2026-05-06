# Competitor model.

import uuid
from sqlalchemy import ForeignKey, String, Text, UUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Competitor(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "competitors"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    business = relationship("Business", back_populates="competitors")

