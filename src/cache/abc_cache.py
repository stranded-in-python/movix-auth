from abc import ABC, abstractmethod


class CacheStorageABC(ABC):
    @abstractmethod
    async def get(self, key: str) -> bytes | bytearray | memoryview | None:
        ...

    @abstractmethod
    async def set(self, key: str, value: bytes | bytearray | memoryview | None):
        ...


class TokenBlacklistStorageABC(ABC):
    # @abstractmethod
    # async def get_token(self, token: str):
    #     ...
    
    @abstractmethod
    async def add_to_set(self, set_name: str, value: bytes | memoryview | str | int | float):
        ...

    @abstractmethod
    async def is_in_set(self, set_name: str, value: bytes | memoryview | str | int | float):
        ...
    
    @abstractmethod
    async def destroy_set(self, set_name: str):
        ...

    @abstractmethod
    async def remove_from_set(set_name: str, value: bytes | memoryview | str | int | float):
        ...