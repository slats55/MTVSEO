# AgentTask model.

import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import AgentTaskStatus

class AgentTask(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agent_tasks"

    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    business_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    website_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    status: Mapped[AgentTaskStatus] = mapped_column(
        Enum(AgentTaskStatus), default=AgentTaskStatus.PENDING, nullable=False
    )
    input_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
    result_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    # Relationships
    creator = relationship("User", back_populates="agent_tasks")
    run_logs = relationship("AgentRunLog", back_populates="task", cascade="all, delete-orphan")
