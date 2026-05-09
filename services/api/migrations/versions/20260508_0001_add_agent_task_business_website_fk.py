"""Add AgentTask business_id and website_id foreign keys

Revision ID: 20260508_0001
Revises: 20260507_0001
Create Date: 2026-05-08 00:01:00.000000

This migration adds two missing ForeignKey constraints to the agent_tasks table:
- business_id → businesses.id  (SET NULL on delete, nullable column)
- website_id  → websites.id     (SET NULL on delete, nullable column)

These constraints were present in the ORM model but missing from the Alembic
migration, allowing PostgreSQL to accept orphaned business/website UUIDs.

WARNING: If production data contains agent_tasks rows with non-NULL business_id
or website_id values that do not reference valid businesses.id or websites.id rows,
this migration will FAIL with a foreign key violation. In that case, orphaned
rows must be cleaned up before this migration can apply.

This migration does NOT delete or modify any data — it only adds constraints.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260508_0001"
down_revision: Union[str, None] = "20260507_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add FK constraint on agent_tasks.business_id → businesses.id
    op.create_foreign_key(
        "fk_agent_tasks_business_id",
        "agent_tasks",
        "businesses",
        ["business_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # Add FK constraint on agent_tasks.website_id → websites.id
    op.create_foreign_key(
        "fk_agent_tasks_website_id",
        "agent_tasks",
        "websites",
        ["website_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_agent_tasks_website_id",
        "agent_tasks",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_agent_tasks_business_id",
        "agent_tasks",
        type_="foreignkey",
    )