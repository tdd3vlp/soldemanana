"""update_subscription_tiers_to_free_premium

Revision ID: 3ba85f6edff3
Revises: 001_initial
Create Date: 2026-05-25 15:42:04.076125

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3ba85f6edff3'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE users SET subscription_tier = 'free' WHERE subscription_tier IN ('basic', 'pro')")
    op.execute("UPDATE subscriptions SET tier = 'free' WHERE tier IN ('basic', 'pro')")


def downgrade() -> None:
    pass
