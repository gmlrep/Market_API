from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class AsyncSessionLocal(AsyncSession):
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, db_url: str | None = None) -> None:
        self._async_engine = create_async_engine(
            url=db_url or settings.db_settings.db_url,
            echo=settings.db_settings.echo,
            pool_size=settings.db_settings.POOL_SIZE,
            max_overflow=settings.db_settings.POOL_OVERFLOW,
            pool_timeout=settings.db_settings.POOL_TIMEOUT,
            pool_pre_ping=True,
        )
        self._async_session_factory = async_sessionmaker(
            class_=AsyncSessionLocal,
            bind=self._async_engine,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._async_session_factory() as session:
            yield session
