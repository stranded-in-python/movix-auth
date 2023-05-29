import uuid
from typing import TYPE_CHECKING, AsyncGenerator

from fastapi import Depends
from sqlalchemy import ForeignKey, MetaData, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.config import settings
from db.access_rights import (
    SQLAlchemyAccessRightDatabase,
    SQLAlchemyBaseAccessRightUUID,
    SQLAlchemyBaseRoleAccessRightTableUUID,
    SQLAlchemyRoleAccessRightDatabase,
)
from db.roles import (
    SQLAlchemyBaseRoleTableUUID,
    SQLAlchemyBaseUserRoleTableUUID,
    SQLAlchemyRoleDatabase,
    SQLAlchemyUserRoleDatabase,
)
from db.tokens import SQLAlchemyAccessTokenDatabase, SQLAlchemyBaseAccessTokenTableUUID
from db.users import (
    SQLAlchemyBaseSignInHistoryTableUUID,
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)

DATABASE_URL = settings.database_url_async
UUID = uuid.UUID
metadata_obj = MetaData(schema="users")


class Base(DeclarativeBase):
    metadata = metadata_obj


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
        signin = relationship("SignInHistory")


class SignInHistory(SQLAlchemyBaseSignInHistoryTableUUID, Base):
    if TYPE_CHECKING:
        user_id: UUID

    else:
        user_id: Mapped[UUID] = mapped_column("user", ForeignKey("user.id"))


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass


class Role(SQLAlchemyBaseRoleTableUUID, Base):
    pass


class UserRole(SQLAlchemyBaseUserRoleTableUUID, Base):
    pass


class AccessRight(SQLAlchemyBaseAccessRightUUID, Base):
    pass


class RoleAccessRight(SQLAlchemyBaseRoleAccessRightTableUUID, Base):
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
    yield SQLAlchemyUserDatabase(session, User, SignInHistory)


async def get_role_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyRoleDatabase(session, Role)


async def get_user_role_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserRoleDatabase(session, UserRole)


async def get_access_right_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyAccessRightDatabase(session, AccessRight)


async def get_access_token_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


async def get_access_rights_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyAccessRightDatabase(session, AccessRight)


async def get_role_access_right_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyRoleAccessRightDatabase(session, RoleAccessRight)
