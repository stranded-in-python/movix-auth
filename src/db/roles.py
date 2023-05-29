import uuid
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import Select

from core.pagination import PaginateQueryParams
from db.base import BaseRoleDatabase, BaseUserRoleDatabase
from db.generics import GUID
from db.models import ID, RP, URP

UUID_ID = uuid.UUID
TRow = TypeVar("TRow")


class SQLAlchemyBaseRoleTable(Generic[ID]):
    """Base SQLAlchemy roles table definition."""

    __tablename__ = "role"

    id: ID
    name: Mapped[str] = mapped_column(String(length=100), nullable=False, index=True)


class SQLAlchemyBaseRoleTableUUID(SQLAlchemyBaseRoleTable[UUID_ID]):
    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)


class SQLAlchemyRoleDatabase(BaseRoleDatabase[RP, ID]):
    session: AsyncSession
    user_table: Type[RP]

    def __init__(self, session: AsyncSession, role_table: Type[RP]):
        self.session = session
        self.role_table = role_table

    @cache_decorator
    async def search(
        self, pagination_params: PaginateQueryParams, filter_param: str | None = None
    ) -> list[TRow]:
        statement = select(self.role_table)
        if filter_param:
            statement.where(
                self.role_table.name == filter_param
            )

        statement.limit(pagination_params.page_size)
        statement.offset(
            (pagination_params.page_number - 1) * pagination_params.page_size
        )

        results = await self.session.execute(statement)

        return results.fetchall()

    @cache_decorator
    async def get_by_id(self, role_id: ID) -> Optional[RP]:
        statement = select(
            self.role_table
        ).where(
            self.role_table.id == role_id
        )
        return await self._get_role(statement)

    @cache_decorator
    async def get_by_name(self, name: str) -> Optional[RP]:
        statement = select(
            self.role_table
        ).where(
            func.lower(self.role_table.name) == func.lower(name)
        )
        return await self._get_role(statement)

    async def create(self, create_dict: Dict[str, Any]) -> RP:
        role = self.role_table(**create_dict)
        self.session.add(role)
        await self.session.commit()
        return role

    async def update(self, role: RP, update_dict: Dict[str, Any]) -> RP:
        for key, value in update_dict.items():
            setattr(role, key, value)
        self.session.add(role)
        await self.session.commit()
        return role

    async def delete(self, role_id: ID) -> None:
        statement = select(
            self.role_table
        ).where(
            self.role_table.id == role_id
        )
        role_to_delete = await self._get_role(statement)
        await self.session.delete(role_to_delete)
        await self.session.commit()

    async def _get_role(self, statement: Select) -> Optional[RP]:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()


class SQLAlchemyBaseUserRoleTableUUID:
    __tablename__ = "user_role"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID_ID] = mapped_column(
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


class SQLAlchemyUserRoleDatabase(BaseUserRoleDatabase[URP, ID]):
    session: AsyncSession
    user_role_table: Type[URP]

    def __init__(
        self,
        session: AsyncSession,
        user_role_table: Type[URP]
        
    ):
        self.session = session
        self.user_role_table = user_role_table

    @cache_decorator
    async def get_user_role(self, user_id: ID, role_id: ID) -> Optional[URP]:
        statement = select(
            self.user_role_table
        ).where(
            (self.user_role_table.user_id == user_id)
            & (self.user_role_table.role_id == role_id)
        )

        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def assign_user_role(self, update_dict: Dict[str, Any]) -> URP:
        user_role = self.user_role_table(**update_dict)

        self.session.add(user_role)
        await self.session.commit()

        return user_role

    async def remove_user_role(self, user_role: URP) -> None:
        instance = await self.get_user_role(
            user_role.user_id,
            user_role.role_id
        )

        await self.session.delete(instance)
        await self.session.commit()

    @cache_decorator
    async def get_user_roles(self, user_id: ID) -> Optional[list[URP]]:
        statement = select(
            self.user_role_table
        ).where(
            self.user_role_table.user_id == user_id
        )
        results = await self.session.execute(statement)

        return results.fetchall()
