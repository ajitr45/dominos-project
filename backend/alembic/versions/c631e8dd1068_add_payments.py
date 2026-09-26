"""add payments

Revision ID: c631e8dd1068
Revises: 4f1f33df3ef2
Create Date: 2026-09-27 00:21:20.961251

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c631e8dd1068'
down_revision: Union[str, Sequence[str], None] = '4f1f33df3ef2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'payments',

        sa.Column('id', sa.Integer(), nullable=False),

        sa.Column(
            'order_id',
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            'user_id',
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            'amount',
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            'method',
            sa.Enum(
                'cod',
                'online',
                name='paymentmethod',
            ),
            nullable=False,
        ),

        sa.Column(
            'status',
            sa.Enum(
                'pending',
                'paid',
                'failed',
                'refunded',
                name='paymentstatus',
            ),
            nullable=False,
        ),

        sa.Column(
            'transaction_id',
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ['order_id'],
            ['orders.id'],
        ),

        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),

        sa.CheckConstraint(
            'amount >= 0',
            name='ck_payments_amount_non_negative',
        ),

        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index(
        op.f('ix_payments_id'),
        'payments',
        ['id'],
        unique=False,
    )

    op.create_index(
        op.f('ix_payments_order_id'),
        'payments',
        ['order_id'],
        unique=True,
    )

    op.create_index(
        op.f('ix_payments_status'),
        'payments',
        ['status'],
        unique=False,
    )

    op.create_index(
        op.f('ix_payments_transaction_id'),
        'payments',
        ['transaction_id'],
        unique=True,
    )

    op.create_index(
        op.f('ix_payments_user_id'),
        'payments',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f('ix_payments_user_id'),
        table_name='payments',
    )

    op.drop_index(
        op.f('ix_payments_transaction_id'),
        table_name='payments',
    )

    op.drop_index(
        op.f('ix_payments_status'),
        table_name='payments',
    )

    op.drop_index(
        op.f('ix_payments_order_id'),
        table_name='payments',
    )

    op.drop_index(
        op.f('ix_payments_id'),
        table_name='payments',
    )

    op.drop_table('payments')