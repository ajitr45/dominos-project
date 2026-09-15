"""add sizes and size relationship

Revision ID: 421c78ba9fd3
Revises: 2c494e3c4ccf
Create Date: 2026-09-15 13:13:17.605223

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "421c78ba9fd3"
down_revision: Union[str, Sequence[str], None] = "2c494e3c4ccf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ---------------------------------------------------------
    # 1. Create sizes table
    # ---------------------------------------------------------

    op.create_table(
        "sizes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "name",
            name="uq_sizes_name",
        ),
    )

    op.create_index(
        "ix_sizes_id",
        "sizes",
        ["id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 2. Insert sizes required by existing data
    # ---------------------------------------------------------

    sizes_table = sa.table(
        "sizes",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
        sa.column("is_active", sa.Boolean()),
    )

    op.bulk_insert(
        sizes_table,
        [
            {
                "id": 1,
                "name": "Small",
                "is_active": True,
            },
            {
                "id": 2,
                "name": "Medium",
                "is_active": True,
            },
            {
                "id": 3,
                "name": "Large",
                "is_active": True,
            },
        ],
    )

    # ---------------------------------------------------------
    # 3. Add size_id temporarily as nullable
    # ---------------------------------------------------------

    op.add_column(
        "product_variants",
        sa.Column(
            "size_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    connection = op.get_bind()

    # ---------------------------------------------------------
    # 4. Migrate existing size values to size_id
    #
    # Example:
    #
    # old:
    # size = "Large"
    #
    # new:
    # size_id = 3
    # ---------------------------------------------------------

    connection.execute(
        sa.text(
            """
            UPDATE product_variants
            SET size_id = (
                SELECT sizes.id
                FROM sizes
                WHERE sizes.name = product_variants.size
            )
            """
        )
    )

    # ---------------------------------------------------------
    # 5. Verify that every existing variant was mapped
    # ---------------------------------------------------------

    result = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM product_variants
            WHERE size_id IS NULL
            """
        )
    )

    missing_count = result.scalar()

    if missing_count != 0:
        raise RuntimeError(
            "Migration stopped: some product variants "
            "could not be mapped to a size."
        )

    # ---------------------------------------------------------
    # 6. Rebuild product_variants using SQLite batch mode
    #
    # SQLite does not support directly adding foreign keys
    # or changing column constraints with ALTER TABLE.
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "product_variants",
        recreate="always",
    ) as batch_op:

        # size_id becomes required
        batch_op.alter_column(
            "size_id",
            existing_type=sa.Integer(),
            nullable=False,
        )

        # Foreign key
        batch_op.create_foreign_key(
            "fk_product_variants_size_id",
            "sizes",
            ["size_id"],
            ["id"],
        )

        # Same product cannot have the same size twice
        batch_op.create_unique_constraint(
            "uq_product_variants_product_size",
            ["product_id", "size_id"],
        )

        # Old size column is no longer required
        batch_op.drop_column("size")


def downgrade() -> None:

    connection = op.get_bind()

    # ---------------------------------------------------------
    # 1. Temporarily add old size column
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "product_variants",
        recreate="always",
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "size",
                sa.String(),
                nullable=True,
            )
        )

    # ---------------------------------------------------------
    # 2. Restore size name from sizes table
    # ---------------------------------------------------------

    connection.execute(
        sa.text(
            """
            UPDATE product_variants
            SET size = (
                SELECT sizes.name
                FROM sizes
                WHERE sizes.id = product_variants.size_id
            )
            """
        )
    )

    # ---------------------------------------------------------
    # 3. Remove new constraints and size_id
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "product_variants",
        recreate="always",
    ) as batch_op:

        batch_op.alter_column(
            "size",
            existing_type=sa.String(),
            nullable=False,
        )

        batch_op.drop_constraint(
            "uq_product_variants_product_size",
            type_="unique",
        )

        batch_op.drop_constraint(
            "fk_product_variants_size_id",
            type_="foreignkey",
        )

        batch_op.drop_column("size_id")

    # ---------------------------------------------------------
    # 4. Remove sizes table
    # ---------------------------------------------------------

    op.drop_index(
        "ix_sizes_id",
        table_name="sizes",
    )

    op.drop_table("sizes")