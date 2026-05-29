"""add users id sequence

Revision ID: 5f2a7c8d9e10
Revises: 4c2f1d8a7b92
Create Date: 2026-05-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "5f2a7c8d9e10"
down_revision: Union[str, None] = "4c2f1d8a7b92"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS users_id_seq")
    op.execute(
        """
        SELECT setval(
            'users_id_seq',
            COALESCE((SELECT MAX(id) FROM users), 0) + 1,
            false
        )
        """
    )
    op.execute("ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq')")
    op.execute("ALTER SEQUENCE users_id_seq OWNED BY users.id")


def downgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS users_id_seq")
