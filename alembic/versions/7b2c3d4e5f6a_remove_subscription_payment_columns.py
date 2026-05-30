"""remove subscription payment columns

Revision ID: 7b2c3d4e5f6a
Revises: 6a1f0b2c3d4e
Create Date: 2026-05-30 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "7b2c3d4e5f6a"
down_revision: str | None = "6a1f0b2c3d4e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("subscriptions", "payment_id")
    op.drop_column("subscriptions", "payment_provider")


def downgrade() -> None:
    op.add_column(
        "subscriptions",
        sa.Column("payment_provider", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "subscriptions",
        sa.Column("payment_id", sa.String(length=256), nullable=True),
    )
