from datetime import datetime
from typing import ClassVar, Protocol, TypeVar
from uuid import UUID


class AccessTokenProtocol(Protocol):
    """Access token protocol that ORM model should follow."""

    token: ClassVar[str]
    user_id: ClassVar[UUID]
    created_at: ClassVar[datetime]

    def __init__(self, *args, **kwargs) -> None:
        ...  # pragma: no cover


AP = TypeVar("AP", bound=AccessTokenProtocol)
