from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

async_engine = create_async_engine(url=settings.db_settings.db_url,
                                   echo=settings.db_settings.echo)
async_session = async_sessionmaker(async_engine,
                                   expire_on_commit=False)


class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
