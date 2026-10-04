"""add payment amount constraint

Revision ID: e54f64394309
Revises: adfce388e4d9
Create Date: 2026-10-03 00:04:26.606014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e54f64394309'
down_revision: Union[str, Sequence[str], None] = 'adfce388e4d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.create_check_constraint("ck_payments_amount_non_negative", "amount >= 0")


def downgrade() -> None:
    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.drop_constraint("ck_payments_amount_non_negative", type_="check")
