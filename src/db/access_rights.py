import uuid
from typing import Any, Iterable, Mapping, Sequence, Tuple

from sqlalchemy import ForeignKey, Row, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import Select

from cache.cache import cache_decorator
from core.pagination import PaginateQueryParams

from . import base, generics
from .schemas import models


class SAAccessRight(base.SQLAlchemyBase):
    """Base SQLAlchemy access_right table definition."""

    __tablename__ = "access_right"

    id: Mapped[uuid.UUID] = mapped_column(
        generics.GUID, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(length=100), nullable=False, index=True)


class SAAccessRightDB(base.BaseAccessRightDatabase[models.AccessRight, uuid.UUID]):
    session: AsyncSession
    access_right_table: type[SAAccessRight]

    def __init__(self, session: AsyncSession, access_right_table: type[SAAccessRight]):
        self.session = session
        self.access_right_table = access_right_table

    async def get_all_access_rights(self) -> Iterable[models.AccessRight] | None:
        statement = select(self.access_right_table)
        access_rights = await self._get_access_rights(statement)
        if not access_rights:
            return None
        return list(models.AccessRight.from_orm(ar) for ar in access_rights)

    async def search(
        self, pagination_params: PaginateQueryParams, filter_param: str | None = None
    ) -> Iterable[models.AccessRight]:
        statement = select(self.access_right_table)
        if filter_param:
            statement.where(self.access_right_table.name == filter_param)

        statement.limit(pagination_params.page_size)
        statement.offset(
            (pagination_params.page_number - 1) * pagination_params.page_size
        )

        results = await self.session.execute(statement)

        return list(
            models.AccessRight.from_orm(result[0]) for result in results.fetchall()
        )

    @cache_decorator()
    async def get(self, access_right_id: uuid.UUID) -> models.AccessRight | None:
        model = self._get_access_right_by_id(access_right_id)

        if model:
            return models.AccessRight.from_orm(model)
        return None

    async def create(self, create_dict: Mapping[str, Any]) -> models.AccessRight:
        access_right = self.access_right_table(**create_dict)
        self.session.add(access_right)
        await self.session.commit()
        return models.AccessRight.from_orm(access_right)

    async def update(
        self, access_right: models.AccessRight, update_dict: Mapping[str, Any]
    ) -> models.AccessRight:
        model = self._get_access_right_by_id(access_right.id)

        for key, value in update_dict.items():
            setattr(model, key, value)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return models.AccessRight.from_orm(model)

    async def delete(self, access_right_id: uuid.UUID) -> None:
        model = self._get_access_right_by_id(access_right_id)

        await self.session.delete(model)
        await self.session.commit()

    async def _get_access_right(
        self, statement: Select[Tuple[SAAccessRight]]
    ) -> SAAccessRight | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def _get_access_right_by_id(
        self, access_right_id: uuid.UUID
    ) -> SAAccessRight | None:
        statement = select(self.access_right_table).where(
            self.access_right_table.id == access_right_id
        )
        return await self._get_access_right(statement)

    async def _get_access_rights(
        self, statement: Select[Tuple[SAAccessRight]]
    ) -> Sequence[Row[Tuple[SAAccessRight]]]:
        results = await self.session.execute(statement)
        if not results:
            return results
        return results.unique().fetchall()

    def __getstate__(self):
        """pickle.dumps()"""
        # Определяем, какие атрибуты должны быть сериализованы
        state = self.__class__.__name__

        return state


class SARoleAccessRight(base.SQLAlchemyBase):
    __tablename__ = "role_access_right"

    id: Mapped[uuid.UUID] = mapped_column(
        generics.GUID, primary_key=True, default=uuid.uuid4
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        generics.GUID,
        ForeignKey("role.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
        index=True,
    )
    access_right_id: Mapped[uuid.UUID] = mapped_column(
        generics.GUID,
        ForeignKey("access_right.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
        index=True,
    )


class SARoleAccessRightDB(
    base.BaseRoleAccessRightDatabase[models.RoleAccessRight, uuid.UUID]
):
    session: AsyncSession
    role_access_right_table: type[SARoleAccessRight]

    def __init__(
        self, session: AsyncSession, role_access_right_table: type[SARoleAccessRight]
    ):
        self.session = session
        self.role_access_right_table = role_access_right_table

    @cache_decorator()
    async def get(
        self, role_id: uuid.UUID, access_right_id: uuid.UUID
    ) -> models.RoleAccessRight | None:
        statement = (
            select(self.role_access_right_table)
            .where(self.role_access_right_table.role_id == role_id)
            .where(self.role_access_right_table.access_right_id == access_right_id)
        )
        model = await self._get_role_access_right(statement)
        if not model:
            return None
        return models.RoleAccessRight.from_orm(model)

    async def create(self, create_dict: Mapping[str, Any]) -> models.RoleAccessRight:
        role_access_right = self.role_access_right_table(**create_dict)
        self.session.add(role_access_right)
        await self.session.commit()
        return models.RoleAccessRight.from_orm(role_access_right)

    async def update(
        self, role_access_right: models.RoleAccessRight, update_dict: Mapping[str, Any]
    ) -> models.RoleAccessRight:
        model = self.get(role_access_right.role_id, role_access_right.access_right_id)
        for key, value in update_dict.items():
            setattr(role_access_right, key, value)
            setattr(model, key, value)
        self.session.add(role_access_right)
        await self.session.commit()
        return role_access_right

    async def delete(self, role_access_right_id: uuid.UUID) -> None:
        statement = select(self.role_access_right_table).where(
            self.role_access_right_table.id == role_access_right_id
        )
        role_access_right = await self._get_role_access_right(statement)
        await self.session.delete(role_access_right)
        await self.session.commit()

    @cache_decorator()
    async def get_all_access_rights_of_user(
        self, role_id: uuid.UUID
    ) -> None | Iterable[models.RoleAccessRight]:
        statement = select(self.role_access_right_table).where(
            self.role_access_right_table.role_id == role_id
        )
        arights = await self._get_role_access_rights(statement)
        if not arights:
            return
        return list(models.RoleAccessRight.from_orm(right) for right in arights)

    async def _get_role_access_right(
        self, statement: Select[Tuple[SARoleAccessRight]]
    ) -> SARoleAccessRight | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def _get_role_access_rights(
        self, statement: Select[Tuple[SARoleAccessRight]]
    ) -> Sequence[Row[Tuple[SARoleAccessRight]]]:
        results = await self.session.execute(statement)
        if not results:
            return results
        return results.unique().fetchall()

    def __getstate__(self):
        """pickle.dumps()"""
        # Определяем, какие атрибуты должны быть сериализованы
        state = self.__class__.__name__

        return state
