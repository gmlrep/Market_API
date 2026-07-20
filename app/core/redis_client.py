import logging

from redis import asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class Redis:
    client: redis.StrictRedis | None = None

    @classmethod
    async def connect(cls) -> None:
        kwargs: dict = {
            "host": settings.redis_settings.host,
            "port": settings.redis_settings.port,
            "decode_responses": True,
        }
        if settings.redis_settings.password:
            kwargs["password"] = settings.redis_settings.password
        try:
            cls.client = redis.StrictRedis(**kwargs)
            await cls.client.ping()
        except redis.RedisError as e:
            logger.error("Failed connection to Redis: %s", e)
            raise

    @classmethod
    async def close(cls) -> None:
        if cls.client is not None:
            await cls.client.aclose()
            cls.client = None

    @classmethod
    async def get(cls, key):
        return await cls.client.get(key)

    @classmethod
    async def set(cls, key, value, expire):
        return await cls.client.set(key, value, expire)

    @classmethod
    async def delete(cls, key):
        return await cls.client.delete(key)
