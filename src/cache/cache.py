from __future__ import annotations

import codecs
import json
import logging
import pickle
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, cast

import cache.utils as utils
from core.config import settings

from .abc_cache import CacheStorageABC
from .redis import RedisClient, get_manager


class CacheError(Exception):
    """
    Базовая ошибка кэширования
    """

    ...


class RedisCacheStorage(CacheStorageABC):
    def __init__(self, redis: RedisClient):
        self._client = redis

    async def get(self, key: str) -> bytes | bytearray | memoryview | None:
        value = await self._client.get(key)
        if not isinstance(value, (bytes, bytearray, memoryview)) and value is not None:
            raise TypeError(f"Failed to get serialized value for key {key}")
        return value

    async def set(self, key: str, value: bytes | bytearray | memoryview | None):
        if not isinstance(value, (bytes, bytearray, memoryview)):
            raise TypeError(
                f"Expected bytes or None value for key {key}, but have {type(value)}"
            )
        return self._client.set(key, value)


class Cache(metaclass=utils.Singleton):
    """
    Класс-обёртка над redis для работы с cache методов.
    """

    def __init__(self, storage: RedisCacheStorage):
        self.storage: RedisCacheStorage = storage

    async def get(self, key: str) -> Any:
        """
        Получить значение из cache по ключу key с отметкой о том, когда было положено
        """
        serialized = await self.storage.get(key)
        if serialized is None:
            return serialized

        value = None
        try:
            if not isinstance(serialized, (bytes, bytearray, memoryview)):
                raise TypeError(f"Failed to deserialize value for key {key}")
            value = pickle.loads(serialized)
        except (TypeError, pickle.PicklingError) as e:
            logging.error(e)
        return value

    async def set(self, key: str, value: Any):
        """
        Положить значение в cache
        """
        try:
            state = pickle.dumps(value)
        except pickle.UnpicklingError as e:
            logging.error(e)
            raise CacheError("Failed to set an object")
        await self.storage.set(key, state)

    @classmethod
    def get_instance(cls) -> Cache | None:
        return cast(Cache, cls._instances.get(cls))


def expired(timestamp: datetime) -> bool:
    delta = timedelta(seconds=settings.cache_expiration_in_seconds)
    if datetime.now() - timestamp >= delta:
        return True

    return False


def is_serializable(thing: Any) -> bool:
    try:
        json.dumps(thing)
    except TypeError:
        return False
    return True


def prepare_key(func: Callable, *args, **kwargs) -> str:
    key = {'callable': func.__name__, 'args': args, 'kwargs': sorted(kwargs.items())}
    serialized = ""
    try:
        serialized = json.dumps(key)
    except TypeError:
        # if can't encode straight to json, we need to encode to base64 first
        if not is_serializable(key['args']):
            key['args'] = codecs.encode(pickle.dumps(key['args']), 'base64').decode()
        if not is_serializable(key['kwargs']):
            key['kwargs'] = codecs.encode(
                pickle.dumps(key['kwargs']), 'base64'
            ).decode()
    serialized = json.dumps(key)
    return serialized


def get_cache() -> Cache:
    """
    Получить инстанс Cache
    """
    cache = Cache.get_instance()
    if cache:
        return cache

    redis_manager = get_manager()
    storage = RedisCacheStorage(redis_manager.get_client())
    return Cache(storage)


def cache_decorator(cache_storage: Cache = get_cache()) -> Callable:
    """
    Декоратор для кэширования результатов вызываемого объекта
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def inner(*args, **kwargs):
            key = prepare_key(func, *args, **kwargs)
            cached_response = await cache_storage.get(key)
            response = cached_response.get('response') if cached_response else None
            if not response or expired(cached_response.get('timestamp')):
                response = await func(*args, **kwargs)
                state = {'timestamp': datetime.now(), 'response': response}
                await cache_storage.set(key, state)
            return response

        return inner

    return decorator
