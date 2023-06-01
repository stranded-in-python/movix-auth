import abc
import uuid
from datetime import datetime
from typing import Any, Dict, Type

from sqlalchemy import ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from authentication.strategy.db.adapter import TokenBlacklistManager
from cache.cache import cache_decorator

from .base import SQLAlchemyBase
from .generics import GUID, TIMESTAMPAware, now_utc
from .schemas import schemas

UUID_ID = uuid.UUID


class SABaseToken:
    """Base SQLAlchemy access token table definition."""

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    token: Mapped[str] = mapped_column(String(length=43), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMPAware(timezone=True), index=True, nullable=False, default=now_utc
    )

    @declared_attr
    def user_id(cls) -> Mapped[GUID]:
        return mapped_column(
            GUID, ForeignKey("user.id", ondelete="cascade"), nullable=False
        )


class SAAccessTokenBlacklist(SABaseToken, SQLAlchemyBase):
    __tablename__ = "access_token_blacklist"


class SARefreshTokenBlacklist(SABaseToken, SQLAlchemyBase):
    __tablename__ = "refresh_token_blacklist"


class SABaseTokenBlacklistDB(TokenBlacklistManager[schemas.Token], abc.ABC):
    """
    Access token database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param access_token_table: SQLAlchemy access token model.
    """

    def __init__(
        self,
        session: AsyncSession,
        access_token_table: Type[SABaseToken and SQLAlchemyBase],
    ):
        self.session = session
        self.access_token_table = access_token_table

    @cache_decorator()
    async def get_by_token(
        self, token: str, max_age: datetime | None = None
    ) -> schemas.Token | None:
        statement = select(self.access_token_table).where(
            self.access_token_table.token == token  # type: ignore
        )
        if max_age is not None:
            statement = statement.where(
                self.access_token_table.created_at >= max_age  # type: ignore
            )

        results = await self.session.execute(statement)
        token_model = results.scalar_one_or_none()
        if not token_model:
            return None
        return schemas.Token.from_orm(token_model)

    async def enlist(self, create_dict: Dict[str, Any]) -> schemas.Token:
        token = self.access_token_table(**create_dict)
        self.session.add(token)
        await self.session.commit()
        return schemas.Token.from_orm(token)

    async def forget(self, access_token: schemas.Token) -> None:
        await self.session.delete(access_token)
        await self.session.commit()


class SAAccessBlacklistDB(SABaseTokenBlacklistDB):
    def __init__(
        self, session: AsyncSession, access_token_table: Type[SAAccessTokenBlacklist]
    ):
        super().__init__(session, access_token_table)


class SARefreshBlacklistDB(SABaseTokenBlacklistDB):
    def __init__(
        self, session: AsyncSession, access_token_table: Type[SAAccessTokenBlacklist]
    ):
        super().__init__(session, access_token_table)
