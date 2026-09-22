"""update user model

Revision ID: e22f629c1ac6
Revises: 421c78ba9fd3
Create Date: 2026-09-18 01:25:15.079414

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e22f629c1ac6"
down_revision: Union[str, Sequence[str], None] = "421c78ba9fd3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    with op.batch_alter_table(
        "users",
        recreate="always",
    ) as batch_op:

        # Add secure password storage
        batch_op.add_column(
            sa.Column(
                "password_hash",
                sa.String(length=255),
                nullable=False,
            )
        )

        # Add timestamps
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
            )
        )

        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
            )
        )

        # Make required user fields non-nullable
        batch_op.alter_column(
            "role",
            existing_type=sa.String(),
            nullable=False,
        )

        batch_op.alter_column(
            "is_active",
            existing_type=sa.Boolean(),
            nullable=False,
        )

        # Username lookup index
        batch_op.create_index(
            "ix_users_username",
            ["username"],
            unique=False,
        )

        # Remove plaintext password column
        batch_op.drop_column("password")


def downgrade() -> None:

    with op.batch_alter_table(
        "users",
        recreate="always",
    ) as batch_op:

        # Restore old password column
        batch_op.add_column(
            sa.Column(
                "password",
                sa.String(),
                nullable=False,
            )
        )

        batch_op.drop_index("ix_users_username")

        batch_op.alter_column(
            "is_active",
            existing_type=sa.Boolean(),
            nullable=True,
        )

        batch_op.alter_column(
            "role",
            existing_type=sa.String(),
            nullable=True,
        )

        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("password_hash")