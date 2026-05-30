import json
from typing import Any

import redis.asyncio as aioredis

from app.config import settings


class RedisClient:
    def __init__(self) -> None:
        self._redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        self._redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.aclose()

    @property
    def client(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError("Redis is not connected. Call connect() first.")
        return self._redis

    async def get(self, key: str) -> Any | None:
        value = await self.client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        serialized = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
        if ttl:
            await self.client.setex(key, ttl, serialized)
        else:
            await self.client.set(key, serialized)

    async def delete(self, *keys: str) -> None:
        await self.client.delete(*keys)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def incr(self, key: str, ttl: int | None = None) -> int:
        value = await self.client.incr(key)
        if ttl and value == 1:
            await self.client.expire(key, ttl)
        return value

    async def expire(self, key: str, ttl: int) -> None:
        await self.client.expire(key, ttl)

    async def ttl(self, key: str) -> int:
        return await self.client.ttl(key)


redis_client = RedisClient()
