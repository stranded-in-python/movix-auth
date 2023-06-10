from datetime import datetime
from typing import Protocol  # pragma: no cover
from typing import Optional


class TokenBlacklistManager(Protocol):
    """Protocol for retrieving, creating and updating access tokens from a database."""

    async def check_token(
        self, encoded_token: str | None, max_age: Optional[datetime] = None
    ) -> bool:
        """Check token in blacklist"""
        ...  # pragma: no cover

    async def enlist(self, encoded_token: str):
        """Enlist a token."""
        ...  # pragma: no cover

    async def forget(self, encoded_token: str):
        """Forget a token."""
        ...  # pragma: no cover
