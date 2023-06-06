from abc import ABC, abstractmethod
from typing import Any, Coroutine


class CacheStorageABC(ABC):
    @abstractmethod
    async def get(self, key: str) -> bytes | bytearray | memoryview | None:
        ...

    @abstractmethod
    async def set(
        self,
        key: str,
        value: bytes | bytearray | memoryview | None
    ) -> Coroutine[Any, Any, bool | None]:
        ...
