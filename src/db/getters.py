import uuid
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_database_url_async, settings

from . import access_rights, base, roles, tokens, users

UUID = uuid.UUID
engine = create_async_engine(get_database_url_async())
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(base.SQLAlchemyBase.metadata.create_all)
        await conn.run_sync(users.SAUser.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield users.SAUserDB(session, users.SAUser, users.SASignInHistory)


async def get_role_db(session: AsyncSession = Depends(get_async_session)):
    yield roles.SARoleDB(session, roles.SARole)


async def get_user_role_db(session: AsyncSession = Depends(get_async_session)):
    yield roles.SAUserRoleDB(session, roles.SAUserRole)


async def get_access_blacklist_db(session: AsyncSession = Depends(get_async_session)):
    yield tokens.SAAccessBlacklistDB(session, tokens.SAAccessTokenBlacklist)


async def get_refresh_blacklist_db(session: AsyncSession = Depends(get_async_session)):
    yield tokens.SARefreshBlacklistDB(session, tokens.SAAccessTokenBlacklist)


async def get_access_rights_db(session: AsyncSession = Depends(get_async_session)):
    yield access_rights.SAAccessRightDB(session, access_rights.SAAccessRight)


async def get_role_access_right_db(session: AsyncSession = Depends(get_async_session)):
    yield access_rights.SARoleAccessRightDB(session, access_rights.SARoleAccessRight)
