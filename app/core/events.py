import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.core.redis_client import Redis

logger = logging.getLogger(__name__)


def _is_test_env() -> bool:
    env = (os.getenv("ENVIRONMENT") or os.getenv("ENV") or "").lower()
    return env == "test"


@asynccontextmanager
async def lifespan(_app_life: FastAPI):
    if _is_test_env():
        # Tests use InMemoryBackend / mocked Redis — soft-fail connect.
        try:
            await Redis.connect()
            FastAPICache.init(RedisBackend(Redis.client), prefix="fastapi-cache")
        except Exception as e:
            logger.warning("Redis unavailable in test env: %s", e)
        yield
        try:
            await Redis.close()
        except Exception:
            pass
        return

    await Redis.connect()
    FastAPICache.init(RedisBackend(Redis.client), prefix="fastapi-cache")
    logger.info("Redis and FastAPICache initialized")
    yield
    await Redis.close()
    logger.info("Redis connection closed")
