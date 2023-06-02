from abc import ABC, abstractmethod


class CacheStorageABC(ABC):
    @abstractmethod
    async def get(self, key: str) -> bytes | bytearray | memoryview | None:
        ...

    @abstractmethod
    async def set(self, key: str, value: bytes | bytearray | memoryview | None):
        ...
