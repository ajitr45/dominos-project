"""add product variant active status

Revision ID: 2c494e3c4ccf
Revises: 35095c702526
Create Date: 2026-09-15 00:08:46.656728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c494e3c4ccf'
down_revision: Union[str, Sequence[str], None] = '35095c702526'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("product_variants", sa.Column("is_active", sa.Boolean(), nullable=False,
            server_default=sa.true()))


def downgrade() -> None:
    op.drop_column("product_variants", "is_active")