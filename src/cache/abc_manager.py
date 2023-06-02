from __future__ import annotations

from abc import ABC, abstractmethod

from cache.utils import Singleton


class DBClient(ABC):
    @abstractmethod
    async def close(self):
        ...


class DBManager(metaclass=Singleton):
    def __init__(self, client: DBClient):
        self._client = client

    @classmethod
    def get_instance(cls: type[DBManager]):
        return cls._instances.get(cls)

    async def on_shutdown(self):
        await self._client.close()

    @abstractmethod
    async def on_startup(self):
        ...

    def get_client(self) -> DBClient:
        return self._client
