import pytest
import pytest_asyncio
from datetime import date, timedelta
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import Base
from app.core.dependencies import get_async_session
from app.models.booking import BookingModel  # обязательно импортируем модель


@pytest_asyncio.fixture(autouse=True)
async def setup_database(tmp_path: Path):
    """Создаёт временную БД и настраивает зависимости"""
    db_path = tmp_path / 'test_bookings.db'
    test_engine = create_async_engine(
        f'sqlite+aiosqlite:///{db_path}',
        echo=False,
    )
    test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async def get_test_session():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_async_session] = get_test_session

    # Создаём таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Удаляем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    app.dependency_overrides.pop(get_async_session, None)


@pytest_asyncio.fixture
async def client():
    """Асинхронный клиент для тестирования"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


def valid_booking_payload(**overrides):
    """Возвращает словарь с валидными данными для создания брони"""
    payload = {
        'name': 'Иван Петров',
        'phone': '+79161234567',
        'booking_date': str(date.today() + timedelta(days=1)),
        'booking_time': '13:00:00',
        'guests': 4,
    }
    payload.update(overrides)
    return payload