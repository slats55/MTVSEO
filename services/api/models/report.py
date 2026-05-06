# Report model.

import uuid
from sqlalchemy import Enum, Float, ForeignKey, Integer, JSON, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import ReportType

class Report(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "reports"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    seo_score: Mapped[float | None] = mapped_column(Float)
    geo_score: Mapped[float | None] = mapped_column(Float)
    content_score: Mapped[float | None] = mapped_column(Float)
    seo_issues_count: Mapped[int | None] = mapped_column(Integer)
    geo_issues_count: Mapped[int | None] = mapped_column(Integer)
    top_recommendations: Mapped[list | None] = mapped_column(JSON, default=list)
    file_path: Mapped[str | None] = mapped_column(String(500))
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # Relationships
    business = relationship("Business", back_populates="reports")

