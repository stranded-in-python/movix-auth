import os
from typing import AsyncGenerator

from sqlalchemy import MetaData
from fastapi import Depends
from .users import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from .tokens import SQLAlchemyAccessTokenDatabase, SQLAlchemyBaseAccessTokenTableUUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL")

metadata_obj = MetaData(schema="users")

class Base(DeclarativeBase):
    metadata = metadata_obj


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):  
    pass


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_access_token_db(
    session: AsyncSession = Depends(get_async_session),
):  
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)