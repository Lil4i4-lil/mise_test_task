from datetime import date as standard_date
from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import AsyncSessionDep, BookingsPaginationDep
from app.schemas.booking import BookingCreate, BookingOut
from app.services import booking_service


router = APIRouter(prefix='/bookings', tags=['Бронирование'])


@router.post(
    '/',
    summary='Создать новую бронь',
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED
)
async def create_booking(
        db: AsyncSessionDep,
        booking_data: BookingCreate
):
    """Создание новой брони."""
    try:
        new_booking = await booking_service.bookings_create(
            db,
            booking_data
        )
    except booking_service.BookingConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    return new_booking


@router.get(
    '/',
    summary='Получить список всех броней (или за конкретную дату)',
    response_model=list[BookingOut]
)
async def get_bookings(
        db: AsyncSessionDep,
        pagination: BookingsPaginationDep,
        date: standard_date | None = Query(
            None,
            description='Фильтр по дате (YYYY-MM-DD)'
        )
):
    """Получение списка броней с пагинацией
    и возможностью фильтрации по определенной дате."""
    bookings = await booking_service.bookings_list(
        db,
        pagination,
        date
    )
    return bookings


@router.get(
    '/{booking_id}/',
    summary='Получить данные о конкретной брони',
    response_model=BookingOut,
    responses={
        status.HTTP_404_NOT_FOUND: {'description': 'Booking not found'}
    }
)
async def get_booking(
        db: AsyncSessionDep,
        booking_id: int
):
    """Получение информации о конкретной брони по id."""
    booking = await booking_service.bookings_retrieve(
        db,
        booking_id
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Booking not found'
        )
    return booking


@router.delete(
    '/{booking_id}/',
    summary='Отменить бронь',
    response_model=BookingOut,
    responses={
        status.HTTP_404_NOT_FOUND: {'description': 'Booking not found'}
    }
)
async def cancel_booking(
        db: AsyncSessionDep,
        booking_id: int
):
    """Отмена брони (установка поля 'status' в значение 'cancelled')."""
    booking = await booking_service.bookings_cancel(
        db,
        booking_id
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Booking not found'
        )
    return booking
