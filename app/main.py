from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqladmin import Admin

from app.core.config import settings
from app.core.exception_handlers import custom_http_exception_handler
from app.core.redis_client import Redis
from app.db.database import async_engine
from app.admin.admin import auth_backend
from app.admin.views import UserModelView, CategoryModelView, CompanyModelView, OrderModelView, ProductModelView, \
    ReviewModelView
from app.endpoint.customers import customers
from app.endpoint.sellers import sellers
from app.endpoint.auth import users
# from app.middleware.middleware import logging_middleware


@asynccontextmanager
async def lifespan(app_life: FastAPI):
    print('Проверка подключения Redis...')
    await Redis.connect()
    print('Redis запущен и успешно подключен')
    FastAPICache.init(RedisBackend(Redis.client), prefix='fastapi-cache')
    print('Fast-api Cache подключен')
    yield
    await Redis.close()
    print('Соединение с Redis прервано')


app = FastAPI(
    lifespan=lifespan,
    title="Market API",
    summary="Market FastApi project",
    version="0.1.0a",
)


app.include_router(users)
app.include_router(customers)
app.include_router(sellers)

app.add_exception_handler(HTTPException, custom_http_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin = Admin(app, async_engine, authentication_backend=auth_backend)
admin.add_view(UserModelView)
admin.add_view(CategoryModelView)
admin.add_view(CompanyModelView)
admin.add_view(OrderModelView)
admin.add_view(ProductModelView)
admin.add_view(ReviewModelView)

# app.middleware('http')(logging_middleware)
# app.mount('/media', StaticFiles(directory='media'), name='media')

if __name__ == '__main__':
    try:
        uvicorn.run(f"{__name__}:app", port=settings.fast_api_port)
    except KeyboardInterrupt:
        pass
