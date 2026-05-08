# AgentRunLog model.

import uuid
from sqlalchemy import Enum, ForeignKey, Integer, JSON, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import LogLevel

class AgentRunLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agent_run_logs"

    agent_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step: Mapped[str | None] = mapped_column(String(100))
    log_level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel), default=LogLevel.INFO, nullable=False
    )
    message: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    extra_data: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Relationships
    task = relationship("AgentTask", back_populates="run_logs")

