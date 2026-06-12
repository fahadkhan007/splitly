"""add split types and chat

Revision ID: ef310476e22f
Revises: 72cb3aae9e6e
Create Date: 2026-06-13 00:06:05.347015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as PgEnum


# revision identifiers, used by Alembic.
revision: str = 'ef310476e22f'
down_revision: Union[str, Sequence[str], None] = '72cb3aae9e6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Create ENUM types — PostgreSQL has no IF NOT EXISTS for types,
    # so we check pg_type catalog inside a DO block
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'splittype') THEN
                CREATE TYPE splittype AS ENUM ('equal', 'exact', 'percentage', 'shares');
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'expensetype') THEN
                CREATE TYPE expensetype AS ENUM ('group', 'direct');
            END IF;
        END $$;
    """)

    # Step 2: Create expense_messages table — use create_type=False so SQLAlchemy
    # does NOT try to create the ENUM type again during table creation
    op.create_table(
        'expense_messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('expense_id', sa.UUID(), nullable=False),
        sa.Column('expense_type', PgEnum('group', 'direct', name='expensetype', create_type=False), nullable=False),
        sa.Column('sender_id', sa.UUID(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_expense_messages_expense_id'),
        'expense_messages', ['expense_id'], unique=False
    )

    # Step 3: Add columns to existing tables using create_type=False
    op.add_column('direct_expenses', sa.Column(
        'split_type',
        PgEnum('equal', 'exact', 'percentage', 'shares', name='splittype', create_type=False),
        nullable=True
    ))
    op.add_column('direct_expenses', sa.Column('share_value', sa.Numeric(precision=10, scale=4), nullable=True))
    op.execute("UPDATE direct_expenses SET split_type = 'equal' WHERE split_type IS NULL")
    op.alter_column('direct_expenses', 'split_type', nullable=False)

    op.add_column('group_expense_participants', sa.Column(
        'share_value', sa.Numeric(precision=10, scale=4), nullable=True
    ))

    op.add_column('group_expenses', sa.Column(
        'split_type',
        PgEnum('equal', 'exact', 'percentage', 'shares', name='splittype', create_type=False),
        nullable=True
    ))
    op.execute("UPDATE group_expenses SET split_type = 'equal' WHERE split_type IS NULL")
    op.alter_column('group_expenses', 'split_type', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('group_expenses', 'split_type')
    op.drop_column('group_expense_participants', 'share_value')
    op.drop_column('direct_expenses', 'share_value')
    op.drop_column('direct_expenses', 'split_type')
    op.drop_index(op.f('ix_expense_messages_expense_id'), table_name='expense_messages')
    op.drop_table('expense_messages')
    op.execute("DROP TYPE IF EXISTS splittype")
    op.execute("DROP TYPE IF EXISTS expensetype")
