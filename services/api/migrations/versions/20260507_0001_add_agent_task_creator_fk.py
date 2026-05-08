"""Add AgentTask.created_by foreign key

Revision ID: 20260507_0001
Revises: 20260505_1200
Create Date: 2026-05-07 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260507_0001"
down_revision: Union[str, None] = "20260505_1200"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_agent_tasks_created_by",
        "agent_tasks",
        ["created_by"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_agent_tasks_created_by",
        "agent_tasks",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_agent_tasks_created_by",
        "agent_tasks",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_agent_tasks_created_by",
        table_name="agent_tasks",
    )
