import os
import uuid
from typing import AsyncGenerator

from fastapi import Depends

from core.config import settings
from db.access_rights import SQLAlchemyBaseAccessRightTableUUID, SQLAlchemyAccessRightDatabase
from db.roles import SQLAlchemyBaseRoleTableUUID, SQLAlchemyRoleDatabase
from db.users import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = settings.database_url
# TODO Упаковать в env или settings

UUID = uuid.UUID


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass

class Role:
    pass
# class Role(SQLAlchemyBaseRoleTableUUID, Base):
#     pass
# TODO specified __table__ or __tablename__ as User


class AccessRight:
    pass
# class AccessRight(SQLAlchemyBaseAccessRightTableUUID, Base):
#     pass
# TODO specified __table__ or __tablename__ as User


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_role_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyRoleDatabase(session, Role)


async def get_access_right_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyAccessRightDatabase(session, AccessRight)
