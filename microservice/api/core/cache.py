import json
import pickle
from typing import Any

from redis.asyncio import Redis

from core.config import settings

redis: Redis | None = None


async def get_redis() -> Redis:
    global redis

    if redis is None:
        redis = Redis.from_url(
            settings.REDIS_URI,
            encoding="utf-8",
            decode_responses=False,
        )

    return redis


async def set_cache(key: str, value: Any, expiration: int | None = None) -> bool:
    redis_client = await get_redis()

    try:
        serialized_value = json.dumps(value)
    except (TypeError, json.JSONDecodeError):
        try:
            serialized_value = pickle.dumps(value)
        except pickle.PickleError:
            return False

    if expiration:
        return await redis_client.setex(key, expiration, serialized_value)
    else:
        return await redis_client.set(key, serialized_value)


async def get_cache(key: str) -> Any:
    redis_client = await get_redis()

    value = await redis_client.get(key)

    if value is None:
        return None

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        try:
            return pickle.loads(value)
        except pickle.PickleError:
            return value


async def delete_cache(key: str) -> int:
    redis_client = await get_redis()
    return await redis_client.delete(key)


async def flush_cache() -> int:
    redis_client = await get_redis()
    return await redis_client.flushdb()


async def get_cache_keys(pattern: str = '*') -> list[str]:
    redis_client = await get_redis()
    return await redis_client.keys(pattern)
