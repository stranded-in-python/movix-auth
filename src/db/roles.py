import uuid
from typing import Any, Dict, Generic, Optional, Type
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy import Boolean, ForeignKey, Integer, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from ..models import ID, RP, URP
from db.generics import GUID

UUID_ID = uuid.UUID


class SQLAlchemyBaseRoleTable(Generic[ID]):
    """Base SQLAlchemy roles table definition."""

    __tablename__ = "role"

    id: ID
    name: Mapped[str] = mapped_column(
            String(length=100), nullable=False
        )

class SQLAlchemyBaseRoleTableUUID(SQLAlchemyBaseRoleTable[UUID_ID]):
    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)


class SQLAlchemyRoleDatabase:
    session: AsyncSession
    user_table: Type[RP]

    def __init__(
        self,
        session: AsyncSession,
        role_table: Type[RP]
    ):
        self.session = session
        self.role_table = role_table

    async def get_all_roles(self) -> Optional[list[RP]]:
        statement = select(self.role_table)
        return await list(self._get_role(statement)) # ?

    async def get_by_id(self, role_id: ID) -> Optional[RP]:
        statement = select(self.role_table).where(self.role_table.id == role_id)
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
        statement = select(self.role_table).where(self.role_table.id == role_id)
        role_to_delete = await self._get_role(statement)
        await self.session.delete(role_to_delete)
        await self.session.commit()

    async def _get_role(self, statement: Select) -> Optional[RP]:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()


class SQLAlchemyBaseUserRoleTableUUID:
    __tablename__ = "user_role"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: mapped_column(Integer, ForeignKey("user.id", ondelete="cascade", onupdate="cascade"), nullable=False)
    role_id: mapped_column(Integer, ForeignKey("role.id", ondelete="cascade", onupdate="cascade"), nullable=False)


class SQLAlchemyUserRoleDatabase:
    session: AsyncSession
    

    def __init__(
        self,
        session: AsyncSession,
        user_role_table: Type[URP]
        
    ):
        self.session = session
        self.user_role_table = user_role_table

    def check_role(self, user_id: ID, role_id: ID) -> Optional[URP]:
        statement = select(self.role_table).where(
                                        self.user_role_table.user_id == role_id)
        
        return await self._get_role(statement)
