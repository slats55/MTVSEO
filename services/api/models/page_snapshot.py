# PageSnapshot model — one-to-one with Page.

import uuid
from sqlalchemy import JSON, LargeBinary, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class PageSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "page_snapshots"

    page_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    raw_html: Mapped[bytes | None] = mapped_column(LargeBinary)
    html_hash: Mapped[str | None] = mapped_column(String(64))
    extracted_text: Mapped[str | None] = mapped_column(Text)
    structured_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
    http_headers: Mapped[dict | None] = mapped_column(JSON, default=dict)
    screenshot_path: Mapped[str | None] = mapped_column(String(500))

    # Relationships
    page = relationship("Page", back_populates="snapshot")

