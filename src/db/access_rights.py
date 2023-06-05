import uuid
from typing import Any, Iterable, Mapping

from sqlalchemy import ForeignKey, Result, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import Select

from cache.cache import cache_decorator

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
        if access_rights is None:
            return None
        return list(models.AccessRight.from_orm(ar) for ar in access_rights)

    @cache_decorator()
    async def get(self, access_right_id: uuid.UUID) -> None | models.AccessRight:
        statement = select(self.access_right_table).where(
            self.access_right_table.id == access_right_id
        )
        ar = await self._get_access_right(statement)
        return models.AccessRight.from_orm(ar)

    async def create(self, create_dict: Mapping[str, Any]) -> models.AccessRight:
        access_right = self.access_right_table(**create_dict)
        self.session.add(access_right)
        await self.session.commit()
        return models.AccessRight.from_orm(access_right)

    async def update(
        self, access_right: models.AccessRight, update_dict: Mapping[str, Any]
    ) -> models.AccessRight:
        ar_model = self.get(access_right.id)
        for key, value in update_dict.items():
            setattr(ar_model, key, value)
            setattr(access_right, key, value)
        self.session.add(ar_model)
        await self.session.commit()
        return access_right

    async def delete(self, access_right_id: uuid.UUID) -> None:
        statement = select(self.access_right_table).where(
            self.access_right_table.id == access_right_id
        )
        access_right_to_delete = await self._get_access_right(statement)
        await self.session.delete(access_right_to_delete)
        await self.session.commit()

    async def _get_access_right(self, statement: Select) -> None | SAAccessRight:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def _get_access_rights(self, statement: Select) -> None | Result:
        results = await self.session.execute(statement)
        if not results:
            return results
        return results.unique()

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
        arights = await self._get_role_access_right(statement)
        if not arights:
            return
        return list(models.RoleAccessRight.from_orm(right) for right in arights)

    async def _get_role_access_right(
        self, statement: Select
    ) -> None | models.RoleAccessRight:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    def __getstate__(self):
        """pickle.dumps()"""
        # Определяем, какие атрибуты должны быть сериализованы
        state = self.__class__.__name__

        return state
