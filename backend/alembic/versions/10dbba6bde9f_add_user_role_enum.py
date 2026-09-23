"""add user role enum

Revision ID: 10dbba6bde9f
Revises: e22f629c1ac6
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "10dbba6bde9f"
down_revision: Union[str, Sequence[str], None] = "e22f629c1ac6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role_enum = sa.Enum(
    "customer",
    "admin",
    "delivery_boy",
    name="userrole",
)


def upgrade() -> None:
    user_role_enum.create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table("users", recreate="always") as batch_op:
        batch_op.alter_column(
            "role",
            existing_type=sa.String(length=20),
            type_=user_role_enum,
            existing_nullable=False,
            existing_server_default=None,
        )


def downgrade() -> None:
    with op.batch_alter_table("users", recreate="always") as batch_op:
        batch_op.alter_column(
            "role",
            existing_type=user_role_enum,
            type_=sa.String(length=20),
            existing_nullable=False,
        )

    user_role_enum.drop(op.get_bind(), checkfirst=True)