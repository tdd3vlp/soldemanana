"""remove correction explanations

Revision ID: 8c9d0e1f2a3b
Revises: 7b2c3d4e5f6a
Create Date: 2026-05-30 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "8c9d0e1f2a3b"
down_revision: str | None = "7b2c3d4e5f6a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("corrections", "explanation_ru")


def downgrade() -> None:
    op.add_column(
        "corrections",
        sa.Column("explanation_ru", sa.Text(), nullable=False, server_default=""),
    )
    op.alter_column("corrections", "explanation_ru", server_default=None)
