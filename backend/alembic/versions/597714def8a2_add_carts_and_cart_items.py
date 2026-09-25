"""add carts and cart items

Revision ID: 597714def8a2
Revises: 70a136f4b6ad
Create Date: 2026-09-25 22:22:07.365095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '597714def8a2'
down_revision: Union[str, Sequence[str], None] = '70a136f4b6ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ============================================================
    # Create carts table
    # ============================================================

    op.create_table('carts',

        # Primary key
        sa.Column('id', sa.Integer(), nullable=False),

        # Cart belongs to a user
        sa.Column('user_id', sa.Integer(), nullable=False),

        # Only one active cart is allowed per user
        sa.Column('is_active', sa.Boolean(), nullable=False),

        # Cart creation timestamp
        sa.Column('created_at', sa.DateTime(), nullable=False),

        # Cart last update timestamp
        sa.Column('updated_at', sa.DateTime(), nullable=False),

        # Foreign key → users.id
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),

        # Primary key constraint
        sa.PrimaryKeyConstraint('id'),
    )

    # Index for faster ID lookup
    op.create_index(
        op.f('ix_carts_id'),
        'carts',
        ['id'],
        unique=False,
    )

    # Index for filtering active/inactive carts
    op.create_index(
        op.f('ix_carts_is_active'),
        'carts',
        ['is_active'],
        unique=False,
    )

    # Index for finding carts belonging to a user
    op.create_index(
        op.f('ix_carts_user_id'),
        'carts',
        ['user_id'],
        unique=False,
    )

    # ============================================================
    # Production rule:
    # One user can have only ONE active cart.
    #
    # Old/inactive carts can still exist for history.
    # ============================================================

    op.create_index(
        'uq_carts_active_user',
        'carts',
        ['user_id'],
        unique=True,
        sqlite_where=sa.text('is_active = 1'),
    )

    # ============================================================
    # Create cart_items table
    # ============================================================

    op.create_table(
        'cart_items',

        # Primary key
        sa.Column('id', sa.Integer(), nullable=False),

        # Cart reference
        sa.Column('cart_id', sa.Integer(), nullable=False),

        # Product variant reference
        # Example: Farmhouse Pizza → Medium
        sa.Column('product_variant_id', sa.Integer(), nullable=False),

        # Number of items in cart
        sa.Column('quantity', sa.Integer(), nullable=False),

        # Item creation timestamp
        sa.Column('created_at', sa.DateTime(), nullable=False),

        # Item last update timestamp
        sa.Column('updated_at', sa.DateTime(), nullable=False),

        # Foreign key → carts.id
        sa.ForeignKeyConstraint(
            ['cart_id'],
            ['carts.id'],
        ),

        # Foreign key → product_variants.id
        sa.ForeignKeyConstraint(
            ['product_variant_id'],
            ['product_variants.id'],
        ),

        # Primary key
        sa.PrimaryKeyConstraint('id'),

        # Same product variant cannot have multiple rows
        # inside the same cart.
        #
        # Example:
        # Farmhouse Small → quantity 3
        #
        # NOT:
        # Farmhouse Small → quantity 1
        # Farmhouse Small → quantity 2
        sa.UniqueConstraint(
            'cart_id',
            'product_variant_id',
            name='uq_cart_items_cart_variant',
        ),

        # Quantity must always be at least 1
        sa.CheckConstraint(
            'quantity >= 1',
            name='ck_cart_items_quantity_positive',
        ),
    )

    # Index for finding items of a particular cart
    op.create_index(
        op.f('ix_cart_items_cart_id'),
        'cart_items',
        ['cart_id'],
        unique=False,
    )

    # Index for cart item ID lookup
    op.create_index(
        op.f('ix_cart_items_id'),
        'cart_items',
        ['id'],
        unique=False,
    )

    # Index for finding cart items by product variant
    op.create_index(
        op.f('ix_cart_items_product_variant_id'),
        'cart_items',
        ['product_variant_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # ============================================================
    # Remove cart_items indexes
    # ============================================================

    op.drop_index(
        op.f('ix_cart_items_product_variant_id'),
        table_name='cart_items',
    )

    op.drop_index(
        op.f('ix_cart_items_id'),
        table_name='cart_items',
    )

    op.drop_index(
        op.f('ix_cart_items_cart_id'),
        table_name='cart_items',
    )

    # Remove cart_items table
    op.drop_table('cart_items')

    # ============================================================
    # Remove active-cart unique index
    # ============================================================

    op.drop_index(
        'uq_carts_active_user',
        table_name='carts',
    )

    # ============================================================
    # Remove carts indexes
    # ============================================================

    op.drop_index(
        op.f('ix_carts_user_id'),
        table_name='carts',
    )

    op.drop_index(
        op.f('ix_carts_is_active'),
        table_name='carts',
    )

    op.drop_index(
        op.f('ix_carts_id'),
        table_name='carts',
    )

    # Remove carts table
    op.drop_table('carts')