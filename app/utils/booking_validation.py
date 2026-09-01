import re
from datetime import date, time, timedelta


def validate_phone(value: str) -> str:
    """Проверяет формат телефона: +7XXXXXXXXXX или 8XXXXXXXXXX."""
    if not re.fullmatch(r'(\+7|8)\d{10}', value):
        raise ValueError('Телефон должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX')
    return value


def validate_name(value: str) -> str:
    """Проверяет имя: только буквы, пробелы и дефис."""
    if not re.fullmatch(r'[A-Za-zА-Яа-яЁё\s-]+', value):
        raise ValueError('Имя может содержать только буквы, пробелы и дефис')
    return value


def validate_booking_date(value: date) -> date:
    """Проверяет дату: не в прошлом и не позже +90 дней."""
    today = date.today()
    if value < today:
        raise ValueError('Дата бронирования не может быть в прошлом')
    if value > today + timedelta(days=90):
        raise ValueError('Дата бронирования не может быть позже чем через 90 дней')
    return value


def validate_booking_time(value: time) -> time:
    """Проверяет время: целый час и в диапазоне 12:00–22:00."""
    if value.minute != 0 or value.second != 0 or value.microsecond != 0:
        raise ValueError('Время должно быть кратно часу (например, 12:00)')
    if value.hour < 12 or value.hour > 22:
        raise ValueError('Время бронирования должно быть в диапазоне с 12:00 до 22:00')
    return value