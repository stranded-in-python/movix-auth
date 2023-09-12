"""user verification

Revision ID: b108da5dd34c
Revises: 0b4ad69c631c
Create Date: 2023-09-11 19:50:57.653374

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'b108da5dd34c'
down_revision = '0b4ad69c631c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        schema='users',
        table_name='user',
        column=sa.Column(
            name='is_verified',
            type_=sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column(schema='users', table_name='user', column_name='is_verified')
