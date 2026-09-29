"""add user role constraint

Revision ID: 66a522f43073
Revises: 39f5add42524
Create Date: 2026-09-29 01:31:15.506805
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "66a522f43073"
down_revision: Union[str, Sequence[str], None] = "39f5add42524"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Recreate users table with a database-level role constraint.
    with op.batch_alter_table("users") as batch_op:
        batch_op.create_check_constraint(
            "ck_users_role",
            "role IN ('customer', 'admin', 'delivery_boy', 'manager')",
        )


def downgrade() -> None:
    # Remove the database-level role constraint.
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint(
            "ck_users_role",
            type_="check",
        )