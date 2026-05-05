# MetricSnapshot model.

from datetime import date as DateType, datetime

from sqlalchemy import Date, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MetricSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "metric_snapshots"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    snapshot_date: Mapped[DateType] = mapped_column(Date, nullable=False)
    seo_score: Mapped[float | None] = mapped_column(Float)
    geo_score: Mapped[float | None] = mapped_column(Float)
    organic_sessions: Mapped[int | None] = mapped_column(Integer)
    organic_impressions: Mapped[int | None] = mapped_column(Integer)
    organic_clicks: Mapped[int | None] = mapped_column(Integer)
    avg_position: Mapped[float | None] = mapped_column(Float)
    core_web_vitals: Mapped[dict | None] = mapped_column(JSON, default=dict)
    top_keywords: Mapped[list | None] = mapped_column(JSON, default=list)

    # Relationships
    business = relationship("Business", back_populates="metric_snapshots")
