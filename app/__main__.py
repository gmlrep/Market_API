from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqladmin import Admin
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.exceptions import custom_http_exception_handler
from app.core.redis_client import Redis
from app.core.container import Container
from app.utils.class_object import singleton
from app.admin.admin import auth_backend
from app.admin.views import (
    UserModelView,
    CategoryModelView,
    CompanyModelView,
    OrderModelView,
    ProductModelView,
    ReviewModelView,
)
from app.api.v1.routes import routers as v1_routers


@asynccontextmanager
async def lifespan(_app_life: FastAPI):
    try:
        await Redis.connect()
        FastAPICache.init(RedisBackend(Redis.client), prefix="fastapi-cache")
    except Exception:
        pass
    yield
    try:
        await Redis.close()
    except Exception:
        pass


@singleton
class AppCreator:
    def __init__(self):
        self.app = FastAPI(
            lifespan=lifespan,
            **settings.api.set_backend_app_attributes,
        )
        self.container = Container()
        self.db = self.container.db()

        self.app.include_router(router=v1_routers, prefix="/api/v1")

        metrics_app = make_asgi_app()
        self.app.mount("/metrics", metrics_app)

        self.app.add_exception_handler(HTTPException, custom_http_exception_handler)

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors.ALLOWED_ORIGINS,
            allow_credentials=settings.cors.IS_ALLOWED_CREDENTIALS,
            allow_methods=settings.cors.ALLOWED_METHODS,
            allow_headers=settings.cors.ALLOWED_HEADERS,
        )

        @self.app.get("/health")
        def health_check():
            return {"status": "ok"}

        admin = Admin(self.app, self.db._async_engine, authentication_backend=auth_backend)
        admin.add_view(UserModelView)
        admin.add_view(CategoryModelView)
        admin.add_view(CompanyModelView)
        admin.add_view(OrderModelView)
        admin.add_view(ProductModelView)
        admin.add_view(ReviewModelView)


app_creator = AppCreator()
app = app_creator.app
db = app_creator.db
container = app_creator.container

if __name__ == "__main__":
    try:
        uvicorn.run(
            f"{__name__}:app",
            host=settings.server.SERVER_HOST,
            port=settings.server.SERVER_PORT,
        )
    except KeyboardInterrupt:
        pass
