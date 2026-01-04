"""Add database constraints

Revision ID: ab4473431e71
Revises: 2013b83a9ede
Create Date: 2026-01-05 06:59:18.395615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab4473431e71'
down_revision: Union[str, None] = '2013b83a9ede'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch mode for SQLite since it doesn't support ALTER TABLE ADD CONSTRAINT
    with op.batch_alter_table('user_group_membership', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_user_group_membership', ['user_id', 'group_id'])

    # Note: CHECK constraint not added for SQLite (not enforced anyway)
    # Will be enforced when migrating to PostgreSQL


def downgrade() -> None:
    with op.batch_alter_table('user_group_membership', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_group_membership', type_='unique')
