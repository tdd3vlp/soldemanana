"""add basic premium tiers

Revision ID: 6a1f0b2c3d4e
Revises: 5f2a7c8d9e10
Create Date: 2026-05-30 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "6a1f0b2c3d4e"
down_revision: str | None = "5f2a7c8d9e10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE subscription_tier ADD VALUE IF NOT EXISTS 'premium'")
        op.execute("ALTER TYPE subscription_tier_sub ADD VALUE IF NOT EXISTS 'premium'")
    op.execute("UPDATE users SET subscription_tier = 'premium' WHERE subscription_tier = 'pro'")
    op.execute("UPDATE subscriptions SET tier = 'premium' WHERE tier = 'pro'")


def downgrade() -> None:
    op.execute("UPDATE users SET subscription_tier = 'basic' WHERE subscription_tier = 'premium'")
    op.execute("UPDATE subscriptions SET tier = 'basic' WHERE tier = 'premium'")
