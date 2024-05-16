from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.core.exception_handlers import custom_http_exception_handler
from app.core.redis_client import Redis
from app.db.CRUD import BaseCRUD
from app.endpoint.admins import admins
from app.endpoint.customers import customers
from app.endpoint.sellers import sellers
from app.endpoint.users import users
from app.core.config import settings
# from app.middleware.middleware import logging_middleware


# Инициация тестовой базы данных
@asynccontextmanager
async def lifespan(app: FastAPI):
    await BaseCRUD.delete_table()
    print("База отчищена")
    await BaseCRUD.create_table()
    print("База готова к работе")
    yield
    print("Выключение")


@asynccontextmanager
async def lifespan_redis(app_life: FastAPI):
    print('Проверка подключения Redis...')
    await Redis.connect()
    print('Redis запущен и успешно подключен')
    FastAPICache.init(RedisBackend(Redis.client), prefix='fastapi-cache')
    print('Fast-api Cache подключен')
    yield
    await Redis.close()
    print('Соединение с Redis прервано')


app = FastAPI(
    # lifespan=lifespan,
    lifespan=lifespan_redis,
    title="Market API",
    summary="Market FastApi project",
    version="0.1.0a",
)


app.include_router(users)
app.include_router(customers)
app.include_router(sellers)
app.include_router(admins)
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.middleware('http')(logging_middleware)
app.mount('/media', StaticFiles(directory='media'), name='media')

if __name__ == '__main__':
    try:
        uvicorn.run(f"{__name__}:app", port=settings.fast_api_port)
    except KeyboardInterrupt:
        pass
