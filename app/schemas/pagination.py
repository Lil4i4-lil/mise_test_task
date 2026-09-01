from pydantic import BaseModel, Field


class BookingsPaginationParams(BaseModel):
    """Параметры пагинации списка броней."""
    limit: int = Field(10, ge=1, le=100, description='Кол-во броней на странице')
    offset: int = Field(0, ge=0, description='Смещение для пагинации')