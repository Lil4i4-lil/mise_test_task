from datetime import date, time
from sqlalchemy import select, exists

from app.core.dependencies import AsyncSessionDep
from app.models.booking import BookingModel, BookingStatus
from app.schemas.booking import BookingCreate
from app.utils.exceptions import BookingConflictError


async def is_slot_taken(
        db: AsyncSessionDep,
        booking_data: BookingCreate
) -> None:
    """Проверка занятости слота"""
    query = select(
        exists().where(
            BookingModel.booking_date == booking_data.booking_date,
            BookingModel.booking_time == booking_data.booking_time,
        )
    )
    result = await db.execute(query)
    if result.scalar():
        raise BookingConflictError('Слот уже занят')


async def bookings_create(
        db: AsyncSessionDep,
        booking_data: BookingCreate
) -> BookingModel:
    await is_slot_taken(
        db,
        booking_data
    )

    booking = BookingModel(
        **booking_data.model_dump(),
        status=BookingStatus.ACTIVE
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


async def bookings_list(
        db: AsyncSessionDep,
        filter_date: date | None = None
) -> list[BookingModel]:
    query = select(BookingModel)
    if filter_date:
        query = query.where(BookingModel.booking_date == filter_date)
    result = await db.execute(query)
    return list(result.scalars().all())


async def bookings_retrieve(
        db: AsyncSessionDep,
        booking_id: int
) -> BookingModel | None:
    booking = await db.get(
        BookingModel,
        booking_id
    )
    return booking


async def bookings_cancel(
        db: AsyncSessionDep,
        booking_id: int
) -> BookingModel | None:
    booking = await bookings_retrieve(
        db,
        booking_id
    )
    if booking and booking.status == 'active':
        booking.status = BookingStatus.CANCELLED
        await db.commit()
        await db.refresh(booking)
    return booking
