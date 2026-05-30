"""remove legacy message columns

Revision ID: 9e1f0a2b3c4d
Revises: 8c9d0e1f2a3b
Create Date: 2026-05-30 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "9e1f0a2b3c4d"
down_revision: str | None = "8c9d0e1f2a3b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("messages", "scenario_id")
    op.drop_column("messages", "grammar_topic")

    op.execute(
        "UPDATE users SET subscription_tier = 'basic' WHERE subscription_tier = 'pro'"
    )
    op.execute(
        "UPDATE subscriptions SET tier = 'basic' WHERE tier = 'pro'"
    )


def downgrade() -> None:
    op.add_column(
        "messages",
        sa.Column("grammar_topic", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "messages",
        sa.Column("scenario_id", sa.String(length=64), nullable=True),
    )
