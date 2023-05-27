import uuid
from typing import AsyncGenerator, TYPE_CHECKING

from fastapi import Depends

from sqlalchemy import Boolean, ForeignKey, Integer, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy.sql import Select

from core.config import settings
from db.roles import SQLAlchemyBaseRoleTableUUID, SQLAlchemyRoleDatabase
from db.users import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from db.tokens import SQLAlchemyBaseAccessTokenTableUUID, SQLAlchemyAccessTokenDatabase
from db.roles import (SQLAlchemyBaseRoleTableUUID, SQLAlchemyRoleDatabase,
                    SQLAlchemyBaseUserRoleTableUUID, SQLAlchemyUserRoleDatabase)
from db.access_rights import (SQLAlchemyBaseAccessRightUUID, SQLAlchemyAccessRightDatabase,
                     SQLAlchemyBaseUserAccessRightTableUUID, SQLAlchemyUserAccessRightDatabase)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# DATABASE_URL = settings.database_url
DATABASE_URL = 'postgresql+asyncpg://yamp_dummy:qweasd123@localhost:5434/yamp_movies_db'
# TODO Упаковать в env или settings

UUID = uuid.UUID


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    if TYPE_CHECKING:
        username: str
        first_name: str
        last_name: str
    else:
        username: Mapped[str] = mapped_column(
            String(length=20), unique=True, index=True, nullable=False
        )
        first_name: Mapped[str] = mapped_column(
            String(length=32), unique=False, index=True, nullable=False
        )
        last_name: Mapped[str] = mapped_column(
            String(length=32), unique=False, index=True, nullable=False
        )

class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):  
    pass


class Role(SQLAlchemyBaseRoleTableUUID, Base):
    pass


class UserRole(SQLAlchemyBaseUserRoleTableUUID, Base):
    pass


class AccessRight(SQLAlchemyBaseAccessRightUUID, Base):
    pass


class UserAccessRight(SQLAlchemyBaseUserAccessRightTableUUID, Base):
    pass


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(User.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_role_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyRoleDatabase(session, Role)


async def get_user_role_db(
    session: AsyncSession = Depends(get_async_session),
):
    yield SQLAlchemyUserRoleDatabase(session, UserRole)


async def get_access_right_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyAccessRightDatabase(session, AccessRight)


async def get_access_token_db(
    session: AsyncSession = Depends(get_async_session),
):  
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


async def get_access_rights_db(
    session: AsyncSession = Depends(get_async_session),
):
    yield SQLAlchemyAccessRightDatabase(session, AccessRight)


async def get_user_access_right_db(
    session: AsyncSession = Depends(get_async_session),
):
    yield SQLAlchemyUserAccessRightDatabase(session, UserAccessRight)
