import uuid
from typing import Generic

from models import ID

UUID_ID = uuid.UUID


class SQLAlchemyBaseAccessRightTable(Generic[ID]):
    """Base SQLAlchemy access right table definition."""
    pass


class SQLAlchemyBaseAccessRightTableUUID(SQLAlchemyBaseAccessRightTable[UUID_ID]):
    pass
