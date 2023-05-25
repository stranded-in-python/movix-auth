"""initial

Revision ID: 6b618c4c7c55
Revises: 
Create Date: 2023-05-23 22:39:44.099280

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b618c4c7c55'
down_revision = None
branch_labels = None
depends_on = None

# миграции делаются так
def upgrade():
    op.create_table(
        'account',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Unicode(200)),
    )

def downgrade():
    op.drop_table('account')
