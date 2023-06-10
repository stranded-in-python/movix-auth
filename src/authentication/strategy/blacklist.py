import datetime
from functools import lru_cache

from authentication.strategy.adapter import TokenBlacklistManager
from authentication.strategy.base import TokenBlacklistStorage
from cache import redis


class TokenBlacklistRedisStorage(TokenBlacklistStorage):
    def __init__(self, redis: redis.RedisClient, name: str):
        self._client = redis
        self._name = name

    def get_setname(self, name):
        return f'{self._name}_{name}'

    async def add_to_set(self, set_name: str, value: str):
        if not isinstance(value, (str)):
            raise TypeError(f"Expected str value for key, but have {type(value)}")
        await self._client.sadd(self.get_setname(set_name), value)

    async def is_in_set(self, set_name: str, value: str) -> bool:
        if not isinstance(value, (str)):
            raise TypeError(f"Expected str value for key, but have {type(value)}")
        return bool(await self._client.sismember(self.get_setname(set_name), value))

    async def destroy_set(self, set_name: str):
        await self._client.unlink(self.get_setname(set_name))

    async def remove_from_set(self, set_name: str, value: str):
        if not isinstance(value, (str)):
            raise TypeError(f"Expected str value for key, but have {type(value)}")
        await self._client.srem(self.get_setname(set_name), value)


class TokenBlackListRedisManager(TokenBlacklistManager):
    def __init__(self, storage: TokenBlacklistRedisStorage):
        self.storage = storage
        self._date_format = '%Y-%m-%d'

    def _get_yesterday_str(self):
        return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
            self._date_format
        )

    def _get_today_str(self):
        return datetime.datetime.now().strftime(self._date_format)

    async def check_token(self, encoded_token: str | None) -> bool:
        """Check if token in today's and yesterday's blacklist"""
        if not encoded_token:
            return False
        in_yesterday_list = await self.storage.is_in_set(
            self._get_yesterday_str(), encoded_token
        )
        in_today_list = await self.storage.is_in_set(
            self._get_today_str(), encoded_token
        )
        return in_yesterday_list or in_today_list

    async def enlist(self, token: str):
        """Add a token to today's blacklist."""
        await self.storage.add_to_set(self._get_today_str(), token)

    async def destroy(self, name: str | None = None):
        """Forget older blacklist"""
        day_before_yesterday = (
            datetime.datetime.now() - datetime.timedelta(days=2)
        ).strftime(self._date_format)
        setname = day_before_yesterday if not name else name
        await self.storage.destroy_set(setname)

    async def forget(self, token: str):
        """Delete a token from today's blacklist"""
        await self.storage.remove_from_set(self._get_today_str(), token)
        await self.storage.remove_from_set(self._get_yesterday_str(), token)


@lru_cache
def get_manager(name: str) -> TokenBlacklistManager:
    redis_manager = redis.get_manager()
    storage = TokenBlacklistRedisStorage(redis_manager.get_client(), name)
    return TokenBlackListRedisManager(storage)
