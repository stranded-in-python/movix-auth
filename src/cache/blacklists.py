from datetime import timedelta, datetime as dt

from abc_cache import TokenBlacklistStorageABC
from cache.redis import RedisClient, get_manager
from authentication.strategy.adapter import TokenBlacklistManager


class TokenBlacklistRedisStorage(TokenBlacklistStorageABC):
    def __init__(self, redis: RedisClient):
        self._client = redis
        self.set_name = "blacklist_token"

    async def add_to_set(self, set_name: str, value: bytes | memoryview | str | int | float) -> int:
        if not isinstance(value, (bytes, memoryview, str, int, float)):
            raise TypeError(
                f"Expected bytes, str, int, float value for key, but have {type(value)}"
            )
        return self._client.sadd(set_name, value)
        
    async def is_in_set(self, set_name: str, value: bytes | memoryview | str | int | float) -> bool:
        if not isinstance(value, (bytes, memoryview, str, int, float)):
            raise TypeError(
                f"Expected bytes, str, int, float value for key, but have {type(value)}"
            )
        return self._client.sismember(set_name, value)

    async def destroy_set(self, set_name: str) -> int:
        return self._client.unlink(set_name)
    
    async def remove_from_set(self, set_name: str, value: bytes | memoryview | str | int | float):
        if not isinstance(value, (bytes, memoryview, str, int, float)):
            raise TypeError(
                f"Expected bytes, str, int, float value for key, but have {type(value)}"
            )
        return self._client.srem(set_name, value)


class TokenBlackListRedisManager(TokenBlacklistManager):
    def __init__(self, storage: TokenBlacklistRedisStorage):
        self.storage = storage

    async def get_by_token(
        self, token: str
    ) -> int:
        """Check if token in today's blacklist"""
        today = dt.datetime.now().strftime('%Y-%m-%d')
        return await self.storage.is_in_set(today, token)

    async def enlist(self, token: str) -> int:
        """Add a token to today's blacklist."""
        today = dt.datetime.now().strftime('%Y-%m-%d')
        return await self.storage.add_to_set(today, token)
        
    async def forget(self):
        """Forget older blacklist"""
        day_before_yesterday = (dt.datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        return await self.storage.destroy_set(day_before_yesterday)

    async def forget_token(self, token: str) -> None:
        """Delete a token from today's blacklist"""
        today = dt.datetime.now().strftime('%Y-%m-%d')
        return await self.storage.remove_from_set(today, token)
    
