import datetime
from typing import Protocol, TypeVar

from db import models


class AccessTokenProtocol(Protocol[models.ID]):
    """Access token protocol that ORM model should follow."""

    token: str
    user_id: models.ID
    created_at: datetime.datetime


AP = TypeVar("AP", bound=AccessTokenProtocol)
