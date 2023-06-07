from datetime import timedelta, datetime as dt

from abc_cache import TokenBlacklistStorageABC
from cache.redis import RedisClient, get_manager
from authentication.strategy.adapter import TokenBlacklistManager


class TokenBlacklistRedisStorage(TokenBlacklistStorageABC):
    def __init__(self, redis: RedisClient):
        self._client = redis
        self.set_name = "blacklist_token"

    async def add_to_set(self, set_name: str, value: str) -> int:
        if not isinstance(value, (str)):
            raise TypeError(
                f"Expected str value for key, but have {type(value)}"
            )
        return self._client.sadd(set_name, value)
        
    async def is_in_set(self, set_name: str, value: str) -> bool:
        if not isinstance(value, (str)):
            raise TypeError(
                f"Expected str value for key, but have {type(value)}"
            )
        return self._client.sismember(set_name, value)

    async def destroy_set(self, set_name: str) -> int:
        return self._client.unlink(set_name)
    
    async def remove_from_set(self, set_name: str, value: str) -> int:
        if not isinstance(value, (str)):
            raise TypeError(
                f"Expected str value for key, but have {type(value)}"
            )
        return self._client.srem(set_name, value)


class TokenBlackListRedisManager(TokenBlacklistManager):
    def __init__(self, storage: TokenBlacklistRedisStorage):
        self.storage = storage

    async def get_by_token(
        self, token: str
    ) -> int:
        """Check if token in today's and yesterday's blacklist"""
        yesterday = self.storage.is_in_set(
            (dt.datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), token)
        today = self.storage.is_in_set(
            dt.datetime.now().strftime('%Y-%m-%d'), token)
        return yesterday if yesterday >= today else today

    async def enlist(self, token: str) -> int:
        """Add a token to today's blacklist."""
        today = dt.datetime.now().strftime('%Y-%m-%d')
        return await self.storage.add_to_set(today, token)
        
    async def destroy(self) -> int:
        """Forget older blacklist"""
        day_before_yesterday = (dt.datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        return await self.storage.destroy_set(day_before_yesterday)
    
    async def forget(self, token: str) -> int:
        """Delete a token from today's blacklist"""
        today = dt.datetime.now().strftime('%Y-%m-%d')
        return await self.storage.remove_from_set(today, token)

