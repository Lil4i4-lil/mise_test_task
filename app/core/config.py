from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'bookings.db'}"


settings = Settings()
