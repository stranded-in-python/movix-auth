import uuid
from typing import Generic

from models import ID

UUID_ID = uuid.UUID


class SQLAlchemyBaseRoleTable(Generic[ID]):
    """Base SQLAlchemy roles table definition."""
    pass


class SQLAlchemyBaseRoleTableUUID(SQLAlchemyBaseRoleTable[UUID_ID]):
    pass


class SQLAlchemyRoleDatabase:
    ...
