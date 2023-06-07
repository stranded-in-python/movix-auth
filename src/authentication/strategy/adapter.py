from datetime import datetime
from typing import Protocol  # pragma: no cover
from typing import Any, Dict, Generic, Optional

from db import models_protocol as models


class TokenBlacklistManager(Protocol[models.AP]):
    """Protocol for retrieving, creating and updating access tokens from a database."""

    async def get_by_token(
        self, token: str, max_age: Optional[datetime] = None
    ) -> Optional[models.AP]:
        """Get a single access token by token."""
        ...  # pragma: no cover

    async def enlist(self, create_dict: Dict[str, Any]) -> models.AP:
        """Create an access token."""
        ...  # pragma: no cover

    async def forget(self, access_token: models.AP) -> None:
        """Delete an access token."""
        ...  # pragma: no cover
