import uuid
from typing import Any, Iterable, Mapping, TypeVar

from sqlalchemy import ForeignKey, Row, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import Select

from cache.cache import cache_decorator
from core.pagination import PaginateQueryParams

from .base import BaseRoleDatabase, BaseUserRoleDatabase, SQLAlchemyBase
from .generics import GUID
from .schemas import models

UUID_ID = uuid.UUID
TRow = TypeVar("TRow")


class SARole(SQLAlchemyBase):
    """Role table definition."""

    __tablename__ = "role"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(length=100), nullable=False, index=True)


class SARoleDB(BaseRoleDatabase[models.RoleRead, UUID_ID]):
    session: AsyncSession
    user_table: type[SARole]

    def __init__(self, session: AsyncSession, role_table: type[SARole]):
        self.session = session
        self.role_table = role_table

    """Access token protocol that ORM model should follow."""

    @cache_decorator()
    async def search(
        self, pagination_params: PaginateQueryParams, filter_param: str | None = None
    ) -> Iterable[models.RoleRead]:
        statement = select(self.role_table)
        if filter_param:
            statement.where(self.role_table.name == filter_param)

        statement.limit(pagination_params.page_size)
        statement.offset(
            (pagination_params.page_number - 1) * pagination_params.page_size
        )

        results = await self.session.execute(statement)

        return list(
            models.RoleRead.from_orm(result[0]) for result in results.fetchall()
        )

    @cache_decorator()
    async def get_by_id(self, role_id: UUID_ID) -> models.RoleRead | None:
        model = await self._get_role_by_id(role_id)
        if not model:
            return None
        return models.RoleRead.from_orm(model)

    @cache_decorator()
    async def get_multiple(
        self, role_ids: Iterable[uuid.UUID]
    ) -> Iterable[models.AccessRight]:
        if not role_ids:
            return []
        statement = select(self.role_table).where(self.role_table.id.in_(role_ids))
        role_rights = await self._get_roles(statement)

        if not role_rights:
            return []

        return [models.AccessRight.from_orm(right) for right in role_rights]

    @cache_decorator()
    async def get_by_name(self, name: str) -> models.RoleRead | None:
        statement = select(self.role_table).where(
            func.lower(self.role_table.name) == func.lower(name)
        )
        model = await self._get_role(statement)

        if model:
            return models.RoleRead.from_orm(model)
        return None

    async def create(self, create_dict: Mapping[str, Any]) -> models.RoleRead:
        role = self.role_table(**create_dict)
        self.session.add(role)
        await self.session.commit()
        return models.RoleRead.from_orm(role)

    async def update(
        self, role: models.RoleRead, update_dict: Mapping[str, Any]
    ) -> models.RoleRead:
        model = self._get_role_by_id(role.id)

        for key, value in update_dict.items():
            setattr(model, key, value)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return models.RoleRead.from_orm(model)

    async def delete(self, role_id: UUID_ID) -> None:
        statement = select(self.role_table).where(self.role_table.id == role_id)
        role_to_delete = await self._get_role(statement)
        await self.session.delete(role_to_delete)
        await self.session.commit()

    async def _get_role(self, statement: Select[tuple[SARole]]) -> SARole | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def _get_roles(
        self, statement: Select[tuple[SARole]]
    ) -> Iterable[Row[tuple[SARole]]]:
        results = await self.session.execute(statement)
        return results.unique().fetchall()

    async def _get_role_by_id(self, role_id: uuid.UUID) -> SARole | None:
        statement = select(self.role_table).where(self.role_table.id == role_id)
        return await self._get_role(statement)

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


class SAUserRoleDB(BaseUserRoleDatabase[models.UserRole, UUID_ID]):
    session: AsyncSession
    user_role_table: type[SAUserRole]

    def __init__(self, session: AsyncSession, user_role_table: type[SAUserRole]):
        self.session = session
        self.user_role_table = user_role_table

    async def get_user_role(
        self, user_id: UUID_ID, role_id: UUID_ID
    ) -> models.UserRole | None:
        statement = (
            select(self.user_role_table)
            .where(self.user_role_table.user_id == user_id)
            .where(self.user_role_table.role_id == role_id)
        )
        results = await self.session.execute(statement)
        results = results.unique().scalar_one_or_none()

        if not results:
            return None
        return models.UserRole.from_orm(results)

    async def get_user_role_by_id(
        self, user_role_id: UUID_ID
    ) -> models.UserRole | None:
        statement = select(self.user_role_table).where(
            self.user_role_table.id == user_role_id
        )

        results = await self.session.execute(statement)
        if not results:
            return None
        return models.UserRole.from_orm(results.unique().scalar_one_or_none())

    async def assign_user_role(
        self, user_id: UUID_ID, role_id: UUID_ID
    ) -> models.UserRole:
        user_role = self.user_role_table(user_id=user_id, role_id=role_id)

        self.session.add(user_role)
        await self.session.commit()

        return models.UserRole.from_orm(user_role)

    async def remove_user_role(self, user_id: UUID_ID, role_id: UUID_ID) -> None:
        statement = (
            select(self.user_role_table)
            .where(self.user_role_table.user_id == user_id)
            .where(self.user_role_table.role_id == role_id)
        )

        role_to_delete = await self._get_user_role(statement)
        await self.session.delete(role_to_delete)
        await self.session.commit()

    @cache_decorator()
    async def get_user_roles(
        self, user_id: UUID_ID
    ) -> Iterable[models.UserRole] | None:
        statement = (
            select("*")
            .select_from(self.user_role_table)
            .where(self.user_role_table.user_id == user_id)
        )
        result = await self.session.execute(statement)

        if not result:
            return

        return list(models.UserRole.from_orm(row) for row in result.fetchall())

    async def _get_user_role(
        self, statement: Select[tuple[SAUserRole]]
    ) -> SAUserRole | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    def __getstate__(self):
        """pickle.dumps()"""
        # Определяем, какие атрибуты должны быть сериализованы
        state = self.__class__.__name__

        return state
