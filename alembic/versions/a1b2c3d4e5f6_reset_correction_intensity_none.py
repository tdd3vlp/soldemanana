"""reset correction_intensity none to important

Revision ID: a1b2c3d4e5f6
Revises: 9e1f0a2b3c4d
Create Date: 2026-05-30 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "9e1f0a2b3c4d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "UPDATE users SET correction_intensity = 'important' WHERE correction_intensity = 'none'"
    )


def downgrade() -> None:
    pass
