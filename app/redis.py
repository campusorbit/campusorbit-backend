import json
from typing import Any
import logging

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)

# Configure Redis for serverless environment
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=10,  # Smaller pool for serverless
    socket_connect_timeout=5,
    socket_timeout=5,
    socket_keepalive=True,
    socket_keepalive_options={},
    retry_on_timeout=True,
    health_check_interval=30,
)


async def get_cached(key: str) -> Any | None:
    """Get a value from Redis cache."""
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.warning(f"Failed to get cached value for key '{key}': {e}")
        return None


async def set_cached(key: str, value: Any, ttl: int = 60) -> None:
    """Set a value in Redis cache with TTL in seconds."""
    try:
        await redis_client.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as e:
        logger.warning(f"Failed to set cached value for key '{key}': {e}")


async def invalidate_cache(pattern: str) -> None:
    """Delete all cache keys matching pattern."""
    try:
        keys = []
        async for key in redis_client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await redis_client.delete(*keys)
    except Exception as e:
        logger.warning(f"Failed to invalidate cache for pattern '{pattern}': {e}")
