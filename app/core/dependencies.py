from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.schemas.pagination import BookingsPaginationParams


AsyncSessionDep = Annotated[
    AsyncSession,
    Depends(get_async_session)
]
BookingsPaginationDep = Annotated[
    BookingsPaginationParams,
    Depends(BookingsPaginationParams)
]
