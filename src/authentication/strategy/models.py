import datetime
from typing import Protocol

from db import models_protocol


class AccessTokenProtocol(Protocol[models_protocol.ID]):
    """Access token protocol that ORM model should follow."""

    token: str
    user_id: models_protocol.ID
    created_at: datetime.datetime
