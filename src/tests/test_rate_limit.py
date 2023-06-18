from typing import List
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import Depends, FastAPI, HTTPException
from httpx import AsyncClient, Response

from core.config import settings
from rate_limiter import (
    InMemoryBackend,
    RAMBackend,
    RateLimiter,
    RateLimitManager,
    RateLimitTime,
    default_callback,
    default_get_uuid,
    get_uuid_user_id,
)

app = FastAPI()


async def redis_dependency() -> InMemoryBackend:
    return RAMBackend()


@app.get("/limited", dependencies=[Depends(RateLimiter(2, RateLimitTime(seconds=5)))])
async def limited_route():
    return "Got it"


class TestRateLimit(IsolatedAsyncioTestCase):
    testing_uuid: str = "start_uuid"

    async def get_testing_uuid(self, _) -> str:
        return self.testing_uuid

    async def asyncSetUp(self):
        redis = await redis_dependency()
        assert redis is not None
        await RateLimitManager.init(redis, get_uuid=self.get_testing_uuid)

    async def test_rate_limit_manager_init(self):
        redis = AsyncMock()

        await RateLimitManager.init(redis)

        self.assertEqual(RateLimitManager.redis, redis)
        self.assertEqual(RateLimitManager.callback, default_callback)
        self.assertEqual(RateLimitManager.get_uuid, default_get_uuid)

    async def test_rate_limit_time(self):
        rate_limit_time = RateLimitTime(seconds=100)

        self.assertEqual(rate_limit_time.milliseconds, 100 * 1000)

        rate_limit_time = RateLimitTime(minutes=3)

        self.assertEqual(rate_limit_time.milliseconds, 3 * 60 * 1000)

        rate_limit_time = RateLimitTime(hours=2)

        self.assertEqual(rate_limit_time.milliseconds, 2 * 60 * 60 * 1000)

        rate_limit_time = RateLimitTime(days=5)

        self.assertEqual(rate_limit_time.milliseconds, 5 * 24 * 60 * 60 * 1000)

    async def test_rate_limiter_init(self):
        count = 5
        time = RateLimitTime(seconds=56)

        rate_limiter = RateLimiter(count, time)

        self.assertEqual(rate_limiter.count, count)
        self.assertEqual(rate_limiter.time, time)
        self.assertEqual(rate_limiter.get_uuid, None)
        self.assertEqual(rate_limiter.callback, None)

    async def test_default_callback(self):
        with self.assertRaises(HTTPException):
            await default_callback({})

    async def test_default_get_uuid(self):
        host_ip = "111.222.333.444"
        request = AsyncMock()
        request.client.host = host_ip

        uuid = await default_get_uuid(request)

        self.assertIsInstance(uuid, str)
        self.assertEqual(uuid, host_ip)

    @patch("rate_limiter.rate_limit.decode_jwt")
    async def test_get_uuid_user_id(self, decode_jwt: AsyncMock):
        request = MagicMock()
        request.headers.get.return_value = "Bearer test_bearer_token"
        decode_jwt.return_value = {"sub": "5"}

        uuid = await get_uuid_user_id(request)

        decode_jwt.assert_called_once_with(
            "test_bearer_token", settings.access_token_secret, ['movix:auth'], ['HS256']
        )
        self.assertEqual(uuid, "5")

    @patch("rate_limiter.rate_limit.decode_jwt")
    @patch("rate_limiter.rate_limit.HTTPBearer")
    async def test_get_uuid_user_id_no_token(
        self, http_bearer_patch: AsyncMock, decode_jwt_patch: AsyncMock
    ):
        http_bearer_patch.return_value = AsyncMock()
        http_bearer_patch.return_value.return_value = None
        request = MagicMock()

        with self.assertRaises(Exception):
            await get_uuid_user_id(request)

    @patch("rate_limiter.rate_limit.RATE_LIMITS", True)
    async def test_limited_route(self):
        self.testing_uuid = "test_limited_route"

        async with AsyncClient(app=app, base_url="https://test") as ac:
            response: Response = await ac.get("/limited")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), '"Got it"')

    @patch("rate_limiter.rate_limit.RATE_LIMITS", True)
    async def test_limited_route_without_init(self):
        self.testing_uuid = "test_limited_route_without_init"
        RateLimitManager.redis = None  # type: ignore

        with self.assertRaises(Exception):
            async with AsyncClient(app=app, base_url="https://test") as ac:
                await ac.get("/limited")

        redis = await redis_dependency()
        assert redis is not None
        RateLimitManager.redis = redis

    @patch("rate_limiter.rate_limit.RATE_LIMITS", True)
    async def test_spam_limited_route_with_async_callback(self):
        self.testing_uuid = "test_spam_limited_route_with_async_callback"
        async_callback = AsyncMock()
        RateLimitManager.callback = async_callback

        async with AsyncClient(app=app, base_url="https://test") as ac:
            response = None  # type: ignore
            i = 0
            for i in range(4):
                response: Response = await ac.get("/limited")
            assert response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode("utf-8"), '"Got it"')
            if i >= 2:
                async_callback.assert_called()

        RateLimitManager.callback = default_callback

    @patch("rate_limiter.rate_limit.RATE_LIMITS", True)
    async def test_spam_limited_route(self):
        self.testing_uuid = "test_spam_limited_route"
        responses: list[Response] = []

        async with AsyncClient(app=app, base_url="https://test") as ac:
            for _ in range(4):
                responses.append(await ac.get("/limited"))
        for i, response in enumerate(responses):
            if i < 2:
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content.decode("utf-8"), '"Got it"')
            else:
                self.assertEqual(response.status_code, 429)
                self.assertTrue("detail" in response.json())
                self.assertEqual(response.json()["detail"], "Too Many Requests")
