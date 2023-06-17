"""Initial

Revision ID: a1ef3a8ece63
Revises:
Create Date: 2023-06-09 04:25:33.980875

"""
import sqlalchemy as sa

import db.generics
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a1ef3a8ece63'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('CREATE SCHEMA IF NOT EXISTS users;')
    op.create_table(
        'access_right',
        sa.Column('id', db.generics.GUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='users',
    )
    op.create_index(
        op.f('ix_users_access_right_name'),
        'access_right',
        ['name'],
        unique=False,
        schema='users',
    )
    op.create_table(
        'oauth_account',
        sa.Column('id', db.generics.GUID(), nullable=False),
        sa.Column('oauth_name', sa.String(length=100), nullable=False),
        sa.Column('access_token', sa.String(length=1024), nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=True),
        sa.Column('refresh_token', sa.String(length=1024), nullable=True),
        sa.Column('account_id', sa.String(length=320), nullable=False),
        sa.Column('account_email', sa.String(length=320), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='users',
    )
    op.create_index(
        op.f('ix_users_oauth_account_account_id'),
        'oauth_account',
        ['account_id'],
        unique=False,
        schema='users',
    )
    op.create_index(
        op.f('ix_users_oauth_account_oauth_name'),
        'oauth_account',
        ['oauth_name'],
        unique=False,
        schema='users',
    )
    op.create_table(
        'role',
        sa.Column('id', db.generics.GUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='users',
    )
    op.create_index(
        op.f('ix_users_role_name'), 'role', ['name'], unique=False, schema='users'
    )
    op.create_table(
        'user',
        sa.Column('id', db.generics.GUID(), nullable=False),
        sa.Column('username', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('hashed_password', sa.String(length=1024), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('first_name', sa.String(length=32), nullable=True),
        sa.Column('last_name', sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='users',
    )
    op.create_index(
        op.f('ix_users_user_email'), 'user', ['email'], unique=True, schema='users'
    )
    op.create_index(
        op.f('ix_users_user_first_name'),
        'user',
        ['first_name'],
        unique=False,
        schema='users',
    )
    op.create_index(
        op.f('ix_users_user_last_name'),
        'user',
        ['last_name'],
        unique=False,
        schema='users',
    )
    op.create_index(
        op.f('ix_users_user_username'),
        'user',
        ['username'],
        unique=True,
        schema='users',
    )
    op.create_table(
        'access_token_blacklist',
        sa.Column('id', db.generics.GUID(), nullable=False),
        sa.Column('token', sa.String(length=43), nullable=False),
        sa.Column(
            'created_at', db.generics.TIMESTAMPAware(timezone=True), nullable=False
        ),
        sa.Column('user_id', db.generics.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user.id'], ondelete='cascade'),
        sa.PrimaryKeyConstraint('id', 'token'),
        schema='users',
    )
    op.create_index(
        op.f('ix_users_access_token_blacklist_created_at'),
        'access_token_blacklist',
        ['created_at'],
        unique=False,
        schema='users',
    )
    op.create_table(
        'refresh_token_blacklist',
        sa.Column('id', db.generics.GUID(), nullable=False),
        sa.Column('token', sa.String(length=43), nullable=False),
        sa.Column(
            'created_at', db.generics.TIMESTAMPAware(timezone=True), nullable=False
        ),
        sa.Column('user_id', db.generics.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user.id'], ondelete='cascade'),
        sa.PrimaryKeyConstraint('id', 'token'),
        schema='users',
    )
    op.create_index(
        op.f('ix_users_refresh_token_blacklist_created_at'),
        'refresh_token_blacklist',
        ['created_at'],
        unique=False,
        schema='users',
    )
    op.create_table(
        'role_access_right',
        sa.Column('id', db.generics.GUID(), nullable=False),
        sa.Column('role_id', db.generics.GUID(), nullable=False),
        sa.Column('access_right_id', db.generics.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['access_right_id'],
            ['users.access_right.id'],
            onupdate='cascade',
            ondelete='cascade',
        ),
        sa.ForeignKeyConstraint(
            ['role_id'], ['users.role.id'], onupdate='cascade', ondelete='cascade'
        ),
        sa.PrimaryKeyConstraint('id'),
        schema='users',
    )
    op.create_index(
        op.f('ix_users_role_access_right_access_right_id'),
        'role_access_right',
        ['access_right_id'],
        unique=False,
        schema='users',
    )
    op.create_index(
        op.f('ix_users_role_access_right_role_id'),
        'role_access_right',
        ['role_id'],
        unique=False,
        schema='users',
    )
    op.create_table(
        'signins_history',
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('id', db.generics.GUID(), nullable=False),
        sa.Column('fingerprint', sa.String(length=1024), nullable=False),
        sa.Column('user', db.generics.GUID(), nullable=False),
        sa.ForeignKeyConstraint(['user'], ['users.user.id']),
        sa.PrimaryKeyConstraint('timestamp', 'id'),
        sa.UniqueConstraint('timestamp', 'user', 'fingerprint', name='uix_1'),
        postgresql_partition_by='RANGE (timestamp)',
        schema='users',
    )
    op.create_index(
        op.f('ix_sih_timestamp_id'),
        'signins_history',
        ['timestamp', 'id'],
        unique=True,
        schema='users',
    )
    op.create_index(
        op.f('ix_sih_timestamp_user_fingerprint'),
        'signins_history',
        ['timestamp', 'user', 'fingerprint'],
        unique=True,
        schema='users',
    )
    op.execute(
        """CREATE TABLE signins_history_2023 PARTITION OF signins_history
        FOR VALUES FROM ('2023-01-01 00:00:00') TO ('2023-12-31 23:59:59')
    """
    )
    op.execute(
        """CREATE TABLE signins_history_2024 PARTITION OF signins_history
        FOR VALUES FROM ('2024-01-01 00:00:00') TO ('2024-12-31 23:59:59')
    """
    )
    op.execute(
        """CREATE TABLE signins_history_2025 PARTITION OF signins_history
        FOR VALUES FROM ('2025-01-01 00:00:00') TO ('2025-12-31 23:59:59')
    """
    )
    op.create_table(
        'user_role',
        sa.Column('id', db.generics.GUID(), nullable=False),
        sa.Column('user_id', db.generics.GUID(), nullable=False),
        sa.Column('role_id', db.generics.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['role_id'], ['users.role.id'], onupdate='cascade', ondelete='cascade'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.user.id'], onupdate='cascade', ondelete='cascade'
        ),
        sa.PrimaryKeyConstraint('id'),
        schema='users',
    )
    op.create_index(
        op.f('ix_users_user_role_role_id'),
        'user_role',
        ['role_id'],
        unique=False,
        schema='users',
    )
    op.create_index(
        op.f('ix_users_user_role_user_id'),
        'user_role',
        ['user_id'],
        unique=False,
        schema='users',
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f('ix_users_user_role_user_id'), table_name='user_role', schema='users'
    )
    op.drop_index(
        op.f('ix_users_user_role_role_id'), table_name='user_role', schema='users'
    )
    op.drop_table('user_role', schema='users')
    op.drop_table('signins_history', schema='users')
    op.drop_index(
        op.f('ix_users_role_access_right_role_id'),
        table_name='role_access_right',
        schema='users',
    )
    op.drop_index(
        op.f('ix_users_role_access_right_access_right_id'),
        table_name='role_access_right',
        schema='users',
    )
    op.drop_table('role_access_right', schema='users')
    op.drop_index(
        op.f('ix_users_refresh_token_blacklist_created_at'),
        table_name='refresh_token_blacklist',
        schema='users',
    )
    op.drop_table('refresh_token_blacklist', schema='users')
    op.drop_index(
        op.f('ix_users_access_token_blacklist_created_at'),
        table_name='access_token_blacklist',
        schema='users',
    )
    op.drop_table('access_token_blacklist', schema='users')
    op.drop_index(op.f('ix_users_user_username'), table_name='user', schema='users')
    op.drop_index(op.f('ix_users_user_last_name'), table_name='user', schema='users')
    op.drop_index(op.f('ix_users_user_first_name'), table_name='user', schema='users')
    op.drop_index(op.f('ix_users_user_email'), table_name='user', schema='users')
    op.drop_table('user', schema='users')
    op.drop_index(op.f('ix_users_role_name'), table_name='role', schema='users')
    op.drop_table('role', schema='users')
    op.drop_index(
        op.f('ix_users_oauth_account_oauth_name'),
        table_name='oauth_account',
        schema='users',
    )
    op.drop_index(
        op.f('ix_users_oauth_account_account_id'),
        table_name='oauth_account',
        schema='users',
    )
    op.drop_table('oauth_account', schema='users')
    op.drop_index(
        op.f('ix_users_access_right_name'), table_name='access_right', schema='users'
    )
    op.drop_table('access_right', schema='users')
    # ### end Alembic commands ###
