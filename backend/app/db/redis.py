"""Redis client abstraction."""
import redis.asyncio as aioredis
from app.core.config import settings


class RedisClient:
    def __init__(self):
        self._client: aioredis.Redis | None = None

    async def connect(self):
        self._client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> aioredis.Redis:
        if not self._client:
            raise RuntimeError("Redis not connected")
        return self._client

    async def set(self, key: str, value: str, ex: int | None = None):
        return await self.client.set(key, value, ex=ex)

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def delete(self, key: str):
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def incr(self, key: str) -> int:
        return await self.client.incr(key)

    async def expire(self, key: str, seconds: int):
        return await self.client.expire(key, seconds)


redis_client = RedisClient()
