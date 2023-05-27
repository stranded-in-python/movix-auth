import uuid
from typing import Any, Dict, Generic, Optional, Type
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from models import ID, ARP, UARP
from db.generics import GUID

UUID_ID = uuid.UUID


class SQLAlchemyBaseAccessRightTable(Generic[ID]):
    """Base SQLAlchemy access_right table definition."""

    __tablename__ = "access_rights"

    id: ID
    name: Mapped[str] = mapped_column(
            String(length=100), nullable=False
        )

class SQLAlchemyBaseAccessRightUUID(SQLAlchemyBaseAccessRightTable[UUID_ID]):
    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)


class SQLAlchemyAccessRightDatabase:
    session: AsyncSession
    access_right_table: Type[ARP]

    def __init__(
        self,
        session: AsyncSession,
        access_right_table: Type[ARP]
    ):
        self.session = session
        self.access_right_table = access_right_table

    async def get_all_access_rights(self) -> Optional[list[ARP]]:
        statement = select(self.access_right_table)
        return await list(self._get_access_right(statement)) # ?

    async def get_by_id(self, access_right_id: ID) -> Optional[ARP]:
        statement = select(self.access_right_table).where(self.access_right_table.id == access_right_id)
        return await self._get_access_right(statement)

    async def create(self, create_dict: Dict[str, Any]) -> ARP:
        access_right = self.access_right_table(**create_dict)
        self.session.add(access_right)
        await self.session.commit()
        return access_right

    async def update(self, access_right: ARP, update_dict: Dict[str, Any]) -> ARP:
        for key, value in update_dict.items():
            setattr(access_right, key, value)
        self.session.add(access_right)
        await self.session.commit()
        return access_right

    async def delete(self, access_right_id: ID) -> None:
        statement = select(self.access_right_table).where(self.access_right_table.id == access_right_id)
        access_right_to_delete = await self._get_access_right(statement)
        await self.session.delete(access_right_to_delete)
        await self.session.commit()

    async def _get_access_right(self, statement: Select) -> Optional[ARP]:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()


class SQLAlchemyBaseUserAccessRightTableUUID:
    __tablename__ = "user_access_right"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: mapped_column(Integer, ForeignKey("user.id", ondelete="cascade", onupdate="cascade"), nullable=False)
    access_right_id: mapped_column(Integer, ForeignKey("access_right.id", ondelete="cascade", onupdate="cascade"), nullable=False)


class SQLAlchemyUserAccessRightDatabase:
    session: AsyncSession
    user_access_right_table: Type[UARP]

    def __init__(
        self,
        session: AsyncSession,
        user_access_right_table: Type[UARP]
        
    ):
        self.session = session
        self.user_access_right_table = user_access_right_table

    async def get_user_access_right(self, user_id: ID, access_right_id: ID) -> Optional[UARP]:
        statement = select(self.user_access_right_table).where(
                                        (self.user_access_right_table.user_id == user_id) &
                                        self.user_access_right_table.access_right_id == access_right_id)
        return self._get_user_access_right(statement)
    
    async def update(self, access_right: UARP, update_dict: Dict[str, Any]) -> UARP:
        for key, value in update_dict.items():
            setattr(access_right, key, value)
        self.session.add(access_right)
        await self.session.commit()
        return access_right

    async def delete(self, access_right: UARP) -> None:
        await self.session.delete(access_right)
        await self.session.commit()

    async def get_all_access_rights_of_user(self, user_id: ID) -> Optional[list[UARP]]:
        statement = select(self.user_access_right_table).where(self.user_access_right_table.user_id == user_id)
        return await list(self._get_user_access_right(statement)) # ?    

    async def _get_user_access_right(self, statement: Select) -> Optional[UARP]:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()
