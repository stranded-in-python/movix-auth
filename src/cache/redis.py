from typing import Optional

from redis.asyncio import Redis

from core.config import settings

from .abc_manager import DBClient, DBManager

redis: Optional[Redis] = None


class RedisClient(Redis, DBClient):
    """
    Обёртка для redis
    """

    ...


class RedisManager(DBManager):
    """
    Singleton для обертки соединения к Redis
    """

    def __init__(self, client: RedisClient):
        super().__init__(client)
        self._client: RedisClient

    def get_client(self) -> RedisClient:
        return self._client

    async def on_startup(self):
        await self._client.ping()


def get_manager() -> RedisManager:
    """
    Метод для получения инстанса менеджера
    """

    manager: RedisManager | None = RedisManager.get_instance()
    if manager is None:
        manager = RedisManager(
            RedisClient(host=settings.redis_host, port=settings.redis_port)
        )
    return manager