"""add category timestamps and description

Revision ID: daf3d2b2edcc
Revises: 10dbba6bde9f
Create Date: 2026-09-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "daf3d2b2edcc"
down_revision: Union[str, Sequence[str], None] = "10dbba6bde9f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column(
        "categories",
        sa.Column("description", sa.String(length=500), nullable=True),
    )

    op.add_column(
        "categories",
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.add_column(
        "categories",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Fill existing rows with current timestamp
    op.execute(
        sa.text(
            """
            UPDATE categories
            SET created_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            """
        )
    )

    # Make timestamp columns NOT NULL
    with op.batch_alter_table("categories") as batch_op:
        batch_op.alter_column("created_at", nullable=False)
        batch_op.alter_column("updated_at", nullable=False)
        batch_op.alter_column("is_active", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("categories") as batch_op:
        batch_op.alter_column("is_active", nullable=True)

    op.drop_column("categories", "updated_at")
    op.drop_column("categories", "created_at")
    op.drop_column("categories", "description")