import uuid
from typing import Any, Dict, Optional, TypeVar, cast

from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import Select

from cache.cache import cache_decorator
from core.pagination import PaginateQueryParams

from .base import BaseRoleDatabase, BaseUserRoleDatabase, SQLAlchemyBase
from .generics import GUID
from .models import RP, URP, URUP

UUID_ID = uuid.UUID
TRow = TypeVar("TRow")


class SARole(SQLAlchemyBase):
    """Role table definition."""

    __tablename__ = "role"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(length=100), nullable=False, index=True)


class SARoleDB(BaseRoleDatabase[RP, UUID_ID]):
    session: AsyncSession
    user_table: type[SARole]

    def __init__(self, session: AsyncSession, role_table: type[SARole]):
        self.session = session
        self.role_table = role_table

    @cache_decorator()
    async def search(
        self, pagination_params: PaginateQueryParams, filter_param: str | None = None
    ) -> list[RP]:
        statement = select(self.role_table)
        if filter_param:
            statement.where(self.role_table.name == filter_param)

        statement.limit(pagination_params.page_size)
        statement.offset(
            (pagination_params.page_number - 1) * pagination_params.page_size
        )

        results = await self.session.execute(statement)

        return cast(list[RP], list(results.fetchall()))

    @cache_decorator()
    async def get_by_id(self, role_id: UUID_ID) -> RP | None:
        statement = select(self.role_table).where(self.role_table.id == role_id)
        return await self._get_role(statement)

    @cache_decorator()
    async def get_by_name(self, name: str) -> RP | None:
        statement = select(self.role_table).where(
            func.lower(self.role_table.name) == func.lower(name)
        )
        return await self._get_role(statement)

    async def create(self, create_dict: Dict[str, Any]) -> RP:
        role = self.role_table(**create_dict)
        self.session.add(role)
        await self.session.commit()
        return cast(RP, role)

    async def update(self, role: RP, update_dict: Dict[str, Any]) -> RP:
        for key, value in update_dict.items():
            setattr(role, key, value)
        self.session.add(role)
        await self.session.commit()
        return role

    async def delete(self, role_id: UUID_ID) -> None:
        statement = select(self.role_table).where(self.role_table.id == role_id)
        role_to_delete = await self._get_role(statement)
        await self.session.delete(role_to_delete)
        await self.session.commit()

    async def _get_role(self, statement: Select) -> RP | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    def __getstate__(self):
        """pickle.dumps()"""
        # Определяем, какие атрибуты должны быть сериализованы
        state = self.__class__.__name__

        return state


class SAUserRole(SQLAlchemyBase):
    __tablename__ = "user_role"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("user.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[UUID_ID] = mapped_column(
        GUID,
        ForeignKey("role.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
        index=True,
    )


class SAUserRoleDB(BaseUserRoleDatabase[URP, URUP, UUID_ID]):
    session: AsyncSession
    user_role_table: type[SAUserRole]

    def __init__(self, session: AsyncSession, user_role_table: type[SAUserRole]):
        self.session = session
        self.user_role_table = user_role_table

    @cache_decorator()
    async def get_user_role(self, user_id: UUID_ID, role_id: UUID_ID) -> URP | None:
        statement = select(self.user_role_table).where(
            (self.user_role_table.user_id == user_id)
            & (self.user_role_table.role_id == role_id)
        )

        results = await self.session.execute(statement)
        return cast(URP | None, results.unique().scalar_one_or_none())

    async def assign_user_role(self, user_id: UUID_ID, role_id: UUID_ID) -> URP:
        user_role = self.user_role_table(user_id=user_id, role_id=role_id)

        self.session.add(user_role)
        await self.session.commit()

        return cast(URP, user_role)

    async def remove_user_role(self, user_role: URP) -> None:
        instance = await self.get_user_role(user_role.user_id, user_role.role_id)

        await self.session.delete(instance)
        await self.session.commit()

    @cache_decorator()
    async def get_user_roles(self, user_id: UUID_ID) -> list[URP] | None:
        statement = select(self.user_role_table).where(
            self.user_role_table.user_id == user_id
        )
        results = await self.session.execute(statement)

        if not results:
            return

        return cast(list[URP], list(results.fetchall()))

    def __getstate__(self):
        """pickle.dumps()"""
        # Определяем, какие атрибуты должны быть сериализованы
        state = self.__class__.__name__

        return state
