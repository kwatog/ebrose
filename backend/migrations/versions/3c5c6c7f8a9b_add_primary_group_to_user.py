"""Add primary group to user

Revision ID: 3c5c6c7f8a9b
Revises: ab4473431e71
Create Date: 2026-01-05 07:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c5c6c7f8a9b'
down_revision: Union[str, None] = 'ab4473431e71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('primary_group_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_user_primary_group_id', 'user_group', ['primary_group_id'], ['id'])
        batch_op.create_index('ix_user_primary_group_id', ['primary_group_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('ix_user_primary_group_id')
        batch_op.drop_constraint('fk_user_primary_group_id', type_='foreignkey')
        batch_op.drop_column('primary_group_id')
