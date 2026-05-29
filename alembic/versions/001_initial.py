"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-05-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=True),
        sa.Column('first_name', sa.String(length=64), nullable=False),
        sa.Column('last_name', sa.String(length=64), nullable=True),
        sa.Column('level', sa.Enum('A0', 'A1', 'A2', 'B1', 'B2', 'C1', name='language_level'), nullable=True),
        sa.Column('goal', sa.Enum('relocation', 'tourism', 'work', 'communication', name='learning_goal'), nullable=True),
        sa.Column('correction_intensity', sa.Enum('all', 'important', 'none', name='correction_intensity'), nullable=False, server_default='important'),
        sa.Column('subscription_tier', sa.Enum('free', 'basic', 'pro', name='subscription_tier'), nullable=False, server_default='free'),
        sa.Column('is_onboarded', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('messages_today', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_message_date', sa.Date(), nullable=True),
        sa.Column('total_messages', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=False)

    op.create_table(
        'messages',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('mode', sa.Enum('conversation', 'correction', 'scenarios', 'grammar', name='bot_mode'), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', name='message_role'), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('corrected_text', sa.Text(), nullable=True),
        sa.Column('scenario_id', sa.String(length=64), nullable=True),
        sa.Column('grammar_topic', sa.String(length=64), nullable=True),
        sa.Column('has_errors', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_user_id'), 'messages', ['user_id'], unique=False)

    op.create_table(
        'corrections',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('message_id', sa.BigInteger(), nullable=False),
        sa.Column('error_type', sa.String(length=64), nullable=False),
        sa.Column('original_fragment', sa.Text(), nullable=False),
        sa.Column('corrected_fragment', sa.Text(), nullable=False),
        sa.Column('explanation_ru', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_corrections_message_id'), 'corrections', ['message_id'], unique=False)

    op.create_table(
        'vocabulary',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('word', sa.String(length=256), nullable=False),
        sa.Column('translation', sa.Text(), nullable=False),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('source_message_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'word', name='uq_user_word')
    )
    op.create_index(op.f('ix_vocabulary_user_id'), 'vocabulary', ['user_id'], unique=False)

    op.create_table(
        'subscriptions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('tier', sa.Enum('free', 'basic', 'pro', name='subscription_tier_sub'), nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('payment_provider', sa.String(length=64), nullable=True),
        sa.Column('payment_id', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_subscriptions_user_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_vocabulary_user_id'), table_name='vocabulary')
    op.drop_table('vocabulary')
    op.drop_index(op.f('ix_corrections_message_id'), table_name='corrections')
    op.drop_table('corrections')
    op.drop_index(op.f('ix_messages_user_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_table('users')
    
    op.execute(sa.text('DROP TYPE IF EXISTS message_role'))
    op.execute(sa.text('DROP TYPE IF EXISTS bot_mode'))
    op.execute(sa.text('DROP TYPE IF EXISTS subscription_tier_sub'))
    op.execute(sa.text('DROP TYPE IF EXISTS subscription_tier'))
    op.execute(sa.text('DROP TYPE IF EXISTS correction_intensity'))
    op.execute(sa.text('DROP TYPE IF EXISTS learning_goal'))
    op.execute(sa.text('DROP TYPE IF EXISTS language_level'))
