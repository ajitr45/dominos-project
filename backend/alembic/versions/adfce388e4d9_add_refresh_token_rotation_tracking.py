"""add refresh token rotation tracking

Revision ID: adfce388e4d9
Revises: 0c651903eea4
Create Date: 2026-10-01 14:23:23.318841

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "adfce388e4d9"
down_revision: Union[str, Sequence[str], None] = "0c651903eea4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("refresh_tokens") as batch_op:
        batch_op.create_foreign_key(
            "fk_refresh_tokens_replaced_by_token_id",
            "refresh_tokens",
            ["replaced_by_token_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("refresh_tokens") as batch_op:
        batch_op.drop_constraint(
            "fk_refresh_tokens_replaced_by_token_id",
            type_="foreignkey",
        )