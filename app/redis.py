import json
from typing import Any

import redis.asyncio as redis

from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_cached(key: str) -> Any | None:
    """Get a value from Redis cache."""
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cached(key: str, value: Any, ttl: int = 60) -> None:
    """Set a value in Redis cache with TTL in seconds."""
    await redis_client.set(key, json.dumps(value, default=str), ex=ttl)


async def invalidate_cache(pattern: str) -> None:
    """Delete all cache keys matching pattern."""
    keys = []
    async for key in redis_client.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        await redis_client.delete(*keys)
