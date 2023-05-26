"""FastAPI Users database adapter for SQLAlchemy."""
import uuid
from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Type

from .base import BaseUserDatabase
from ..models import ID, UP
from sqlalchemy import Boolean, ForeignKey, Integer, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy.sql import Select

from db.generics import GUID

__version__ = "5.0.0"

UUID_ID = uuid.UUID


class SQLAlchemyBaseUserTable(Generic[ID]):
    """Base SQLAlchemy users table definition."""

    __tablename__ = "user"

    if TYPE_CHECKING:
        id: ID
        email: str
        hashed_password: str
        is_active: bool
        is_superuser: bool
    else:
        email: Mapped[str] = mapped_column(
            String(length=320), unique=True, index=True, nullable=False
        )
        hashed_password: Mapped[str] = mapped_column(
            String(length=1024), nullable=False
        )
        is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
        is_superuser: Mapped[bool] = mapped_column(
            Boolean, default=False, nullable=False
        )


class SQLAlchemyBaseUserTableUUID(SQLAlchemyBaseUserTable[UUID_ID]):
    if TYPE_CHECKING:
        id: UUID_ID

    else:
        id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)


class SQLAlchemyBaseOAuthAccountTable(Generic[ID]):
    """Base SQLAlchemy OAuth account table definition."""

    __tablename__ = "oauth_account"

    if TYPE_CHECKING:  # pragma: no cover
        id: ID
        oauth_name: str
        access_token: str
        expires_at: Optional[int]
        refresh_token: Optional[str]
        account_id: str
        account_email: str
    else:
        oauth_name: Mapped[str] = mapped_column(
            String(length=100), index=True, nullable=False
        )
        access_token: Mapped[str] = mapped_column(String(length=1024), nullable=False)
        expires_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        refresh_token: Mapped[Optional[str]] = mapped_column(
            String(length=1024), nullable=True
        )
        account_id: Mapped[str] = mapped_column(
            String(length=320), index=True, nullable=False
        )
        account_email: Mapped[str] = mapped_column(String(length=320), nullable=False)


class SQLAlchemyBaseOAuthAccountTableUUID(SQLAlchemyBaseOAuthAccountTable[UUID_ID]):
    if TYPE_CHECKING:  # pragma: no cover
        id: UUID_ID
        user_id: UUID_ID
    else:
        id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)

        @declared_attr
        def user_id(cls) -> Mapped[GUID]:
            return mapped_column(
                GUID, ForeignKey("user.id", ondelete="cascade"), nullable=False
            )


class SQLAlchemyUserDatabase(Generic[UP, ID], BaseUserDatabase[UP, ID]):
    """
    Database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param user_table: SQLAlchemy user model.
    """

    session: AsyncSession
    user_table: Type[UP]

    def __init__(
        self,
        session: AsyncSession,
        user_table: Type[UP]
    ):
        self.session = session
        self.user_table = user_table

    async def get(self, user_id: ID) -> Optional[UP]:
        statement = select(self.user_table).where(self.user_table.id == user_id)
        return await self._get_user(statement)

    async def get_by_username(self, username: str) -> Optional[UP]:
        statement = select(self.user_table).where(
            func.lower(self.user_table.username) == func.lower(username)
        ) # TODO Fix type error
        return await self._get_user(statement)

    async def create(self, create_dict: Dict[str, Any]) -> UP:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        return user

    async def update(self, user: UP, update_dict: Dict[str, Any]) -> UP:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        return user

    async def delete(self, user: UP) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def _get_user(self, statement: Select) -> Optional[UP]:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()
