from datetime import date, time, datetime
from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.booking import BookingStatus
from app.utils.booking_validation import (
    validate_booking_date,
    validate_booking_time,
    validate_name,
    validate_phone
)


class BookingCreate(BaseModel):
    """Схема запроса на создание брони."""
    name: str = Field(min_length=2, max_length=127)
    phone: str
    booking_date: date
    booking_time: time
    guests: int = Field(ge=1, le=12)

    @field_validator('name')
    @classmethod
    def _validate_name(cls, v: str) -> str:
        """Проверяет имя на допустимые символы."""
        return validate_name(v)

    @field_validator('phone')
    @classmethod
    def _validate_phone(cls, v: str) -> str:
        """Проверяет телефон на соответствие формату."""
        return validate_phone(v)

    @field_validator('booking_date')
    @classmethod
    def _validate_booking_date(cls, v: date) -> date:
        """Проверяет дату бронирования."""
        return validate_booking_date(v)

    @field_validator('booking_time')
    @classmethod
    def _validate_booking_time(cls, v: time) -> time:
        """Проверяет время бронирования."""
        return validate_booking_time(v)

    @model_validator(mode='after')
    def validate_not_past_time_today(self):
        """Запрещает бронирование на прошедшее время сегодняшнего дня."""
        if self.booking_date == date.today():
            now_time = datetime.now().time()
            if self.booking_time <= now_time:
                raise ValueError('Нельзя забронировать столик '
                                 'на прошедшее время сегодня')
        return self


class BookingOut(BookingCreate):
    """Схема ответа с данными брони."""
    id: int
    status: BookingStatus = BookingStatus.ACTIVE

    model_config = {'from_attributes': True}
