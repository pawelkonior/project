import logging
from fastapi import FastAPI

from core.cache import get_redis

logger = logging.getLogger(__name__)


async def startup_handler(app: FastAPI) -> None:
    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("Successfully connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")


async def shutdown_handler(app: FastAPI) -> None:
    try:
        redis = await get_redis()
        await redis.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Failed to close Redis connection: {e}")
