from redis import asyncio as redis

from app.core.config import settings


class Redis:
    client: redis.StrictRedis = None

    @classmethod
    async def connect(cls):
        try:
            cls.client = redis.StrictRedis(
                host=settings.redis_settings.host,
                port=settings.redis_settings.port,
                # password=settings.redis_settings.password,
                decode_responses=True,
            )
            await cls.client.role()
        except redis.RedisError as e:
            print(f'Failed connection to Redis: {e}')
            raise
        await cls.client

    @classmethod
    async def close(cls):
        if cls.client is not None:
            await cls.client.aclose()

    @classmethod
    async def get(cls, key):
        return await cls.client.get(key)

    @classmethod
    async def set(cls, key, value, expire):
        return await cls.client.set(key, value, expire)

    @classmethod
    async def delete(cls, key):
        return await cls.client.delete(key)
