from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False
)

async_session_factory = async_sessionmaker(
    async_engine,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает асинхронную сессию SQLAlchemy."""
    async with async_session_factory() as async_session:
        yield async_session
