"""add_ai_usage_and_learning_memory

Revision ID: 4c2f1d8a7b92
Revises: 3ba85f6edff3
Create Date: 2026-05-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4c2f1d8a7b92"
down_revision: Union[str, None] = "3ba85f6edff3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("memory_summary", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("mistake_summary", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("active_topic", sa.String(length=128), nullable=True))
    op.add_column("users", sa.Column("learned_vocabulary", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("recent_goals", sa.Text(), nullable=True))

    op.create_table(
        "ai_usage",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost_usd", sa.Numeric(10, 6), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_usage_user_id"), "ai_usage", ["user_id"], unique=False)
    op.create_index(op.f("ix_ai_usage_mode"), "ai_usage", ["mode"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_usage_mode"), table_name="ai_usage")
    op.drop_index(op.f("ix_ai_usage_user_id"), table_name="ai_usage")
    op.drop_table("ai_usage")
    op.drop_column("users", "recent_goals")
    op.drop_column("users", "learned_vocabulary")
    op.drop_column("users", "active_topic")
    op.drop_column("users", "mistake_summary")
    op.drop_column("users", "memory_summary")
