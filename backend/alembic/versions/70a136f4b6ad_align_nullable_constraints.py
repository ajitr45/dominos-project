"""align nullable constraints

Revision ID: 70a136f4b6ad
Revises: daf3d2b2edcc
Create Date: 2026-09-23 14:13:46.624523
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "70a136f4b6ad"
down_revision: Union[str, Sequence[str], None] = "daf3d2b2edcc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Align categories with the SQLAlchemy model
    with op.batch_alter_table("categories") as batch_op:
        batch_op.alter_column(
            "is_active",
            existing_type=sa.Boolean(),
            nullable=False,
        )
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
        )
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            nullable=False,
        )

    # Align product_variants with the SQLAlchemy model
    with op.batch_alter_table("product_variants") as batch_op:
        batch_op.alter_column(
            "is_available",
            existing_type=sa.Boolean(),
            nullable=False,
        )

    # Align products with the SQLAlchemy model
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "is_veg",
            existing_type=sa.Boolean(),
            nullable=False,
        )
        batch_op.alter_column(
            "is_available",
            existing_type=sa.Boolean(),
            nullable=False,
        )
        batch_op.alter_column(
            "is_active",
            existing_type=sa.Boolean(),
            nullable=False,
        )


def downgrade() -> None:
    # Revert products
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "is_active",
            existing_type=sa.Boolean(),
            nullable=True,
        )
        batch_op.alter_column(
            "is_available",
            existing_type=sa.Boolean(),
            nullable=True,
        )
        batch_op.alter_column(
            "is_veg",
            existing_type=sa.Boolean(),
            nullable=True,
        )

    # Revert product_variants
    with op.batch_alter_table("product_variants") as batch_op:
        batch_op.alter_column(
            "is_available",
            existing_type=sa.Boolean(),
            nullable=True,
        )

    # Revert categories
    with op.batch_alter_table("categories") as batch_op:
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            nullable=True,
        )
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=True,
        )
        batch_op.alter_column(
            "is_active",
            existing_type=sa.Boolean(),
            nullable=True,
        )