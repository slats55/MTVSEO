# Business model.

import uuid
from sqlalchemy import Boolean, ForeignKey, String, Text, Uuid
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Business(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "businesses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    business_type: Mapped[str | None] = mapped_column(String(100))
    location: Mapped[str | None] = mapped_column(String(500))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    is_cannabis: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_ymyl: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="businesses")
    websites = relationship("Website", back_populates="business", cascade="all, delete-orphan")
    competitors = relationship("Competitor", back_populates="business", cascade="all, delete-orphan")
    metric_snapshots = relationship("MetricSnapshot", back_populates="business", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="business", cascade="all, delete-orphan")

