"""add delivery boy foreign key to orders

Revision ID: 82f564172cfe
Revises: 66a522f43073
Create Date: 2026-09-29 13:16:29.329757

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "82f564172cfe"
down_revision: Union[str, Sequence[str], None] = "66a522f43073"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing delivery boy foreign key."""

    with op.batch_alter_table("orders") as batch_op:
        batch_op.create_foreign_key(
            "fk_orders_delivery_boy_id_users",
            "users",
            ["delivery_boy_id"],
            ["id"],
        )


def downgrade() -> None:
    """Remove delivery boy foreign key."""

    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_constraint(
            "fk_orders_delivery_boy_id_users",
            type_="foreignkey",
        )