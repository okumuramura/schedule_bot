"""initial

Revision ID: 0f28af740d95
Revises:
Create Date: 2022-08-25 15:49:29.899325

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0f28af740d95'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('group', sa.String(20), nullable=False, unique=True),
    )
    op.create_table(
        'authors',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100)),
        sa.Column('department', sa.String(5)),
    )
    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(150)),
    )
    types_table = op.create_table(
        'lesson_types',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('type', sa.String(30)),
    )
    op.create_table(
        'schedule',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('overline', sa.Boolean),
        sa.Column('classroom', sa.String(30)),
        sa.Column('corps', sa.String(20), nullable=True),
        sa.Column('weekday', sa.Integer),
        sa.Column('num', sa.Integer),
        sa.Column('group_id', sa.Integer, sa.ForeignKey('groups.id')),
        sa.Column(
            'lesson_id', sa.Integer, sa.ForeignKey('lessons.id'), nullable=False
        ),
        sa.Column(
            'author_id', sa.Integer, sa.ForeignKey('authors.id'), nullable=True
        ),
        sa.Column(
            'lesson_type_id',
            sa.Integer,
            sa.ForeignKey('lesson_types.id'),
            nullable=True,
        ),
    )
    op.create_table(
        'active_users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('tid', sa.Integer, unique=True, nullable=False),
        sa.Column(
            'group_id', sa.Integer, sa.ForeignKey('groups.id'), nullable=True
        ),
        sa.Column('vip', sa.Boolean, default=False),
    )

    lesson_types_str = [
        "лек",
        "практ",
        "лаб",
        "лек+практ",
        "практ+лаб",
        "лек+лаб",
        "практ+лек",
        "лаб+практ",
        "лаб+лек",
    ]
    op.bulk_insert(
        types_table,
        [
            {'id': i, 'type': lesson_type}
            for i, lesson_type in enumerate(lesson_types_str, start=1)
        ],
    )


def downgrade() -> None:
    op.drop_table('schedule')
    op.drop_table('active_users')
    op.drop_table('groups')
    op.drop_table('authors')
    op.drop_table('lessons')
    op.drop_table('lesson_types')
