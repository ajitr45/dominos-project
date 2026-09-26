"""add orders and order items

Revision ID: 4f1f33df3ef2
Revises: 3de9b55509db
Create Date: 2026-09-26 22:46:08.443716

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f1f33df3ef2'
down_revision: Union[str, Sequence[str], None] = '3de9b55509db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'orders',

        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('address_id', sa.Integer(), nullable=False),

        sa.Column(
            'status',
            sa.Enum(
                'pending',
                'confirmed',
                'preparing',
                'out_for_delivery',
                'delivered',
                'cancelled',
                name='orderstatus'
            ),
            nullable=False
        ),

        sa.Column('subtotal', sa.Integer(), nullable=False),
        sa.Column('delivery_fee', sa.Integer(), nullable=False),
        sa.Column('discount', sa.Integer(), nullable=False),
        sa.Column('tax', sa.Integer(), nullable=False),
        sa.Column('total_amount', sa.Integer(), nullable=False),

        sa.Column('recipient_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('address_line1', sa.String(length=255), nullable=False),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('landmark', sa.String(length=150), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('postal_code', sa.String(length=10), nullable=False),

        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),

        sa.ForeignKeyConstraint(
            ['address_id'],
            ['addresses.id']
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id']
        ),

        sa.CheckConstraint(
            'subtotal >= 0',
            name='ck_orders_subtotal_non_negative'
        ),
        sa.CheckConstraint(
            'delivery_fee >= 0',
            name='ck_orders_delivery_fee_non_negative'
        ),
        sa.CheckConstraint(
            'discount >= 0',
            name='ck_orders_discount_non_negative'
        ),
        sa.CheckConstraint(
            'tax >= 0',
            name='ck_orders_tax_non_negative'
        ),
        sa.CheckConstraint(
            'total_amount >= 0',
            name='ck_orders_total_non_negative'
        ),

        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_orders_address_id'),
        'orders',
        ['address_id'],
        unique=False
    )

    op.create_index(
        op.f('ix_orders_id'),
        'orders',
        ['id'],
        unique=False
    )

    op.create_index(
        op.f('ix_orders_status'),
        'orders',
        ['status'],
        unique=False
    )

    op.create_index(
        op.f('ix_orders_user_id'),
        'orders',
        ['user_id'],
        unique=False
    )

    op.create_table(
        'order_items',

        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_variant_id', sa.Integer(), nullable=False),

        sa.Column('product_name', sa.String(length=150), nullable=False),
        sa.Column('size_name', sa.String(length=50), nullable=False),
        sa.Column('unit_price', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('subtotal', sa.Integer(), nullable=False),

        sa.Column('created_at', sa.DateTime(), nullable=False),

        sa.ForeignKeyConstraint(
            ['order_id'],
            ['orders.id']
        ),
        sa.ForeignKeyConstraint(
            ['product_variant_id'],
            ['product_variants.id']
        ),

        sa.CheckConstraint(
            'quantity >= 1',
            name='ck_order_items_quantity_positive'
        ),
        sa.CheckConstraint(
            'unit_price >= 0',
            name='ck_order_items_unit_price_non_negative'
        ),
        sa.CheckConstraint(
            'subtotal >= 0',
            name='ck_order_items_subtotal_non_negative'
        ),

        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_order_items_id'),
        'order_items',
        ['id'],
        unique=False
    )

    op.create_index(
        op.f('ix_order_items_order_id'),
        'order_items',
        ['order_id'],
        unique=False
    )

    op.create_index(
        op.f('ix_order_items_product_variant_id'),
        'order_items',
        ['product_variant_id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f('ix_order_items_product_variant_id'),
        table_name='order_items'
    )

    op.drop_index(
        op.f('ix_order_items_order_id'),
        table_name='order_items'
    )

    op.drop_index(
        op.f('ix_order_items_id'),
        table_name='order_items'
    )

    op.drop_table('order_items')

    op.drop_index(
        op.f('ix_orders_user_id'),
        table_name='orders'
    )

    op.drop_index(
        op.f('ix_orders_status'),
        table_name='orders'
    )

    op.drop_index(
        op.f('ix_orders_id'),
        table_name='orders'
    )

    op.drop_index(
        op.f('ix_orders_address_id'),
        table_name='orders'
    )

    op.drop_table('orders')