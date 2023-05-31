"""FastAPI Users database adapter for SQLAlchemy."""
import uuid
from datetime import datetime
from typing import Any, Dict, Type, cast

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship
from sqlalchemy.sql import Select

from cache.cache import cache_decorator
from core.pagination import PaginateQueryParams

from .base import BaseUserDatabase, SQLAlchemyBase
from .generics import GUID
from .models import ID, SIHE, UP

__version__ = "5.0.0"

UUID_ID = uuid.UUID


class SAUser(SQLAlchemyBase):
    """Base SQLAlchemy users table definition."""

    __tablename__ = "user"
    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(
        String(length=20), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    signin = relationship("SQLAlchemySignInHistoryTable")


class SASignInHistory(SQLAlchemyBase):
    __tablename__ = 'signins_history'

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    user_id: Mapped[UUID_ID] = mapped_column("user", ForeignKey("user.id"))


class SQLAlchemyOAuthAccountTable(SQLAlchemyBase):
    """Base SQLAlchemy OAuth account table definition."""

    __tablename__ = "oauth_account"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    oauth_name: Mapped[str] = mapped_column(
        String(length=100), index=True, nullable=False
    )
    access_token: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    expires_at: Mapped[None | int] = mapped_column(Integer, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(
        String(length=1024), nullable=True
    )
    account_id: Mapped[str] = mapped_column(
        String(length=320), index=True, nullable=False
    )
    account_email: Mapped[str] = mapped_column(String(length=320), nullable=False)


class SAUserDB(BaseUserDatabase[UP, ID, SIHE]):
    """
    Database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param user_table: SQLAlchemy user model.
    """

    session: AsyncSession

    def __init__(
        self,
        session: AsyncSession,
        user_table: Type[SAUser],
        history_table: Type[SASignInHistory],
    ):
        self.session = session
        self.user_table = user_table
        self.history_table = history_table

    @cache_decorator()
    async def get(self, user_id: ID) -> UP | None:
        statement = select(self.user_table).where(self.user_table.id == user_id)
        return await self._get_user(statement)

    @cache_decorator()
    async def get_by_username(self, username: str) -> UP | None:
        statement = select(self.user_table).where(
            func.lower(self.user_table.username) == func.lower(username)
        )
        return await self._get_user(statement)

    @cache_decorator()
    async def get_by_email(self, email: str) -> UP | None:
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == func.lower(email)
        )
        return await self._get_user(statement)

    async def create(self, create_dict: Dict[str, Any]) -> UP:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        return cast(UP, user)

    async def update(self, user: UP, update_dict: Dict[str, Any]) -> UP:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        return user

    async def delete(self, user: UP) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def _get_user(self, statement: Select) -> UP | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def record_in_sighin_history(self, user_id: ID, event: SIHE):
        e = self.history_table(user_id=user_id, **event.__dict__)
        self.session.add(e)
        await self.session.commit()

    @cache_decorator()
    async def get_sign_in_history(
        self, user_id: ID, pagination_params: PaginateQueryParams
    ):
        statement: Select = (
            select(self.history_table)
            .where(self.history_table.user_id == user_id)
            .limit(pagination_params.page_size)
            .offset((pagination_params.page_number - 1) * pagination_params.page_size)
        )

        return await self._get_events(statement)

    async def _get_events(self, statement: Select):
        results = await self.session.execute(statement)

        return results.fetchall()

    def __getstate__(self):
        """pickle.dumps()"""
        # Определяем, какие атрибуты должны быть сериализованы
        state = self.__class__.__name__

        return state
