import asyncio

import pytest
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert

from app.core.config import settings
from app.core.redis_client import Redis
from app.core.security import create_access_token
from app.db.models import Category, Sellers, Users, Companies
from app.main import app as fastapi_app
from app.db.database import async_engine, Base, async_session
from redis import asyncio as redis


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        category1 = Category(name='category1')
        category2 = Category(name='category2')
        category3 = Category(name='category3')
        session.add_all([category1, category2, category3])
        await session.commit()

    await Redis.connect()
    FastAPICache.init(RedisBackend(Redis.client), prefix='fastapi-cache')
    yield
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


transport = ASGITransport(app=fastapi_app)


@pytest.fixture(scope='session')
async def ac():
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='session')
async def authenticated_customer_ac():
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        response = await ac.post('/api/v1/auth/login', params={
            'username': 'user@user.com',
            'password': 'password12'
        })
        assert response.status_code == 200
        assert response.cookies['access_token']
        yield ac


@pytest.fixture(scope='session')
async def authenticated_seller_ac():
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        payload = {'sub': 1, 'role': 2, 'username': 'customer1@customer.com', 'is_active': True,
                   'is_enabled': True, 'is_admin': False, 'is_baned': False}
        access_token = create_access_token(data=payload)
        ac.cookies.set('access_token', access_token)
        assert ac.cookies['access_token']
        yield ac
