"""FastAPI Users database adapter for SQLAlchemy."""
import uuid
from datetime import datetime
from typing import Any, Iterable, Sequence

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Row,
    String,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship
from sqlalchemy.sql import Select

from cache.cache import cache_decorator
from core import exceptions
from core.pagination import PaginateQueryParams
from db.base import BaseUserDatabase, SQLAlchemyBase
from db.generics import GUID
from db.schemas import models

UUID_ID = uuid.UUID


class SAOAuthAccount(SQLAlchemyBase):
    """Base SQLAlchemy OAuth account table definition."""

    __tablename__ = "oauth_account"
    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    oauth_name: Mapped[str] = mapped_column(
        String(length=100), index=True, nullable=False
    )
    access_token: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    expires_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(
        String(length=1024), nullable=True
    )
    account_id: Mapped[str] = mapped_column(
        String(length=320), index=True, nullable=False
    )
    account_email: Mapped[str] = mapped_column(String(length=320), nullable=False)

    @declared_attr
    def user_id(cls) -> Mapped[GUID]:
        return mapped_column(
            GUID, ForeignKey("user.id", ondelete="cascade"), nullable=False
        )


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
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    first_name: Mapped[str] = mapped_column(
        String(length=32), unique=False, index=True, nullable=True
    )
    last_name: Mapped[str] = mapped_column(
        String(length=32), unique=False, index=True, nullable=True
    )
    signin = relationship("SASignInHistory")
    oauth_accounts: Mapped[list[SAOAuthAccount]] = relationship(
        "SAOAuthAccount", lazy="joined"
    )


class SASignInHistory(SQLAlchemyBase):
    __tablename__ = 'signins_history'

    timestamp: Mapped[datetime] = mapped_column(
        DateTime, primary_key=True, nullable=False
    )
    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    fingerprint: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    user_id: Mapped[UUID_ID] = mapped_column("user", ForeignKey("user.id"))

    __table_args__ = (
        UniqueConstraint('timestamp', 'user', 'fingerprint', name='uix_1'),
    )


class SAUserDB(
    BaseUserDatabase[
        models.UserRead,
        uuid.UUID,
        models.EventRead,
        models.OAuthAccount,
        models.UserOAuth,
    ]
):
    """
    Database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param user_table: SQLAlchemy user model.
    """

    session: AsyncSession

    def __init__(
        self,
        session: AsyncSession,
        user_table: type[SAUser],
        history_table: type[SASignInHistory],
        oauth_account_table: type[SAOAuthAccount],
    ):
        self.session = session
        self.user_table = user_table
        self.history_table = history_table
        self.oauth_account_table = oauth_account_table

    @cache_decorator()
    async def get(self, user_id: uuid.UUID) -> models.UserRead | None:
        user_model = await self._get_user_by_id(user_id)

        if user_model:
            return models.UserRead.from_orm(user_model)
        return None

    @cache_decorator()
    async def get_multiple(
        self, user_ids: Iterable[uuid.UUID]
    ) -> Iterable[models.UserRead] | None:
        user_models = await self._get_users_by_ids(user_ids)

        if user_models:
            return [models.UserRead.from_orm(user_model) for user_model in user_models]
        return None

    @cache_decorator()
    async def get_by_username(self, username: str) -> models.UserRead | None:
        statement = select(self.user_table).where(
            func.lower(self.user_table.username) == func.lower(username)
        )
        user_model = await self._get_user(statement)

        if not user_model:
            return None
        return models.UserRead.from_orm(user_model)

    @cache_decorator()
    async def get_by_email(self, email: str) -> models.UserRead | None:
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == func.lower(email)
        )
        user_model = await self._get_user(statement)
        if not user_model:
            return None
        return models.UserRead.from_orm(user_model)

    async def create(self, create_dict: dict[str, Any]) -> models.UserRead:
        user_model = self.user_table(**create_dict)
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)

        return models.UserRead.from_orm(user_model)

    async def update(
        self, user: models.UserRead, update_dict: dict[str, Any]
    ) -> models.UserRead:
        user_model = await self._get_user_by_id(user.id)

        for key, value in update_dict.items():
            setattr(user_model, key, value)
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)

        return models.UserRead.from_orm(user_model)

    async def delete(self, user: models.UserRead) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def _get_user(self, statement: Select[tuple[SAUser]]) -> SAUser | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def _get_users(self, statement: Select[Any]) -> Sequence[Row[Any]] | None:
        results = await self.session.execute(statement)
        return results.fetchall()

    async def _get_user_by_id(self, user_id: uuid.UUID) -> SAUser | None:
        statement = select(self.user_table).where(self.user_table.id == user_id)
        return await self._get_user(statement)

    async def _get_users_by_ids(
        self, user_ids: Iterable[uuid.UUID]
    ) -> Sequence[Row[Any]] | None:
        statement = select(self.user_table).where(self.user_table.id.in_(user_ids))
        return await self._get_users(statement)

    async def _get_oauth_account_by_id(
        self, row_id: uuid.UUID
    ) -> SAOAuthAccount | None:
        statement = select(self.oauth_account_table).where(
            self.oauth_account_table.id == row_id
        )
        results = await self.session.execute(statement)

        return results.unique().scalar_one_or_none()

    async def record_in_sighin_history(
        self, user_id: uuid.UUID, event: models.EventRead
    ):
        e = self.history_table(**event.dict())
        self.session.add(e)
        await self.session.commit()

    @cache_decorator()
    async def get_sign_in_history(
        self,
        user_id: uuid.UUID,
        pagination_params: PaginateQueryParams,
        since: datetime | None = None,
        to: datetime | None = None,
    ) -> Iterable[models.EventRead]:
        if not since:
            since = datetime(datetime.now().year - 1, 1, 1, 0, 0, 0, 0)
        if not to:
            to = datetime.now()
        statement: Select[Any] = (
            select(self.history_table)
            .where(self.history_table.timestamp >= since)
            .where(self.history_table.timestamp <= to)
            .where(self.history_table.user_id == user_id)
            .limit(pagination_params.page_size)
            .offset((pagination_params.page_number - 1) * pagination_params.page_size)
        )

        events = await self._get_events(statement)
        if not events:
            return []
        return list(models.EventRead.from_orm(event[0]) for event in events)

    async def get_by_oauth_account(
        self, oauth: str, account_id: str
    ) -> models.UserOAuth | None:
        statement: Select[Any] = (
            select(self.user_table)
            .join(self.oauth_account_table)
            .where(self.oauth_account_table.oauth_name == oauth)
            .where(self.oauth_account_table.account_id == account_id)
        )
        user = await self._get_user(statement)
        if not user:
            return None
        return models.UserOAuth.from_orm(user)

    async def add_oauth_account(
        self, user: models.UserRead, create_dict: dict[str, Any]
    ) -> models.UserOAuth:
        user_model = await self._get_user_by_id(user.id)
        if user_model is None:
            raise exceptions.UserNotExists

        await self.session.refresh(user_model)
        oauth_account = self.oauth_account_table(**create_dict)
        self.session.add(oauth_account)
        user_model.oauth_accounts.append(oauth_account)
        self.session.add(user_model)

        await self.session.commit()

        return models.UserOAuth.from_orm(user_model)

    async def update_oauth_account(
        self,
        user: models.UserRead,
        oauth_account: models.OAuthAccount,
        update_dict: dict[str, Any],
    ) -> models.UserOAuth:
        user_model = await self._get_user_by_id(user.id)
        oauth_account_model = await self._get_oauth_account_by_id(oauth_account.id)

        for key, value in update_dict.items():
            setattr(oauth_account_model, key, value)
        self.session.add(oauth_account_model)
        await self.session.commit()

        return models.UserOAuth.from_orm(user_model)

    async def _get_events(self, statement: Select[Any]) -> Sequence[Row[Any]]:
        results = await self.session.execute(statement)

        return results.fetchall()

    def __getstate__(self):
        """pickle.dumps()"""
        # Определяем, какие атрибуты должны быть сериализованы
        state = self.__class__.__name__

        return state
