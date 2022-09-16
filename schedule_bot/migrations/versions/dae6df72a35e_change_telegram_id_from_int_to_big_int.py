'''change telegram id from int to big int

Revision ID: dae6df72a35e
Revises: 0f28af740d95
Create Date: 2022-09-16 15:12:02.238661

'''
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'dae6df72a35e'
down_revision = '0f28af740d95'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('active_users', 'tid', type_=sa.BigInteger)


def downgrade() -> None:
    # WARNING: possible data loss!
    op.alter_column('active_users', 'tid', type_=sa.Integer)
