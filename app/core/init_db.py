import asyncio

from app.core.database import async_engine, Base
from app.models.booking import BookingModel


async def init_db() -> dict:
    """Создаёт таблицы в базе данных."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return {
        'success': True,
        'tables': tuple(Base.metadata.tables.keys())
    }


if __name__ == '__main__':
    print(asyncio.run(init_db()))
