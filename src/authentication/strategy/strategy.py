import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional

import core.exceptions as exceptions
import db.models_protocol as models
from db.schemas import generics
from managers.user import BaseUserManager

from .adapter import TokenBlacklistManager
from .base import Strategy


class DatabaseStrategy(
    Strategy[models.UP, models.SIHE],
    Generic[models.UP, models.SIHE, models.AP],
):
    def __init__(
        self,
        database: TokenBlacklistManager[models.AP],
        lifetime_seconds: Optional[int] = None,
    ):
        self.database = database
        self.lifetime_seconds = lifetime_seconds

    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.SIHE],
    ) -> Optional[models.UP]:
        if token is None:
            return None

        max_age = None
        if self.lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=self.lifetime_seconds
            )

        access_token = await self.database.get_by_token(token, max_age)
        if access_token is None:
            return None

        try:
            parsed_id = user_manager.parse_id(access_token.user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(self, user: models.UP) -> str:
        access_token_dict = self._create_access_token_dict(user)
        access_token = await self.database.enlist(access_token_dict)
        return access_token.token

    async def destroy_token(self, token: str, user: models.UP) -> None:
        access_token = await self.database.get_by_token(token)
        if access_token is not None:
            await self.database.forget(access_token)

    def _create_access_token_dict(self, user: models.UP) -> Dict[str, Any]:
        token = secrets.token_urlsafe()
        return {"token": token, "user_id": user.id}
