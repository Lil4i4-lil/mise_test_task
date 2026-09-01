from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.v1.booking import router
from app.core.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы при старте
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix='/api/v1')
