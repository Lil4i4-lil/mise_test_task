import pytest
from datetime import date, timedelta

from tests.conftest import valid_booking_payload


# -----Тесты на создание брони-----
@pytest.mark.asyncio
async def test_create_booking_success(client):
    """Проверяет успешное создание брони с валидными данными."""
    payload = valid_booking_payload()
    response = await client.post("/api/v1/bookings/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data['id'] == 1
    assert data['status'] == 'active'
    assert data['name'] == payload['name']
    assert data['phone'] == payload['phone']
    assert data['booking_date'] == payload['booking_date']
    assert data['booking_time'] == payload['booking_time']
    assert data['guests'] == payload['guests']


@pytest.mark.asyncio
async def test_create_booking_invalid_phone(client):
    """Проверяет, что при невалидном телефоне возвращается 422."""
    payload = valid_booking_payload(phone='12345')
    response = await client.post('/api/v1/bookings/', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_booking_invalid_name(client):
    """Проверяет, что при слишком коротком имени возвращается 422."""
    payload = valid_booking_payload(name='A')
    response = await client.post('/api/v1/bookings/', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_booking_invalid_name_with_digits(client):
    """Проверяет, что при имени с недопустимыми возвращается 422."""
    payload = valid_booking_payload(name='Иван123')
    response = await client.post('/api/v1/bookings/', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_booking_invalid_date_past(client):
    """Проверяет, что при дате в прошлом возвращается 422."""
    yesterday = date.today() - timedelta(days=1)
    payload = valid_booking_payload(booking_date=str(yesterday))
    response = await client.post('/api/v1/bookings/', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_booking_invalid_date_too_far(client):
    """Проверяет, что при дате дальше 90 дней возвращается 422."""
    future = date.today() + timedelta(days=91)
    payload = valid_booking_payload(booking_date=str(future))
    response = await client.post('/api/v1/bookings/', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_booking_invalid_time_not_hour(client):
    """Проверяет, что при времени не кратном часу возвращается 422."""
    payload = valid_booking_payload(booking_time='13:30:00')
    response = await client.post('/api/v1/bookings/', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_booking_invalid_time_out_of_range(client):
    """Проверяет, что при времени вне допустимого диапазона возвращается 422."""
    payload = valid_booking_payload(booking_time='11:00:00')
    response = await client.post('/api/v1/bookings/', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_booking_invalid_guests_too_few(client):
    """Проверяет, что при количестве гостей меньше 1 возвращается 422."""
    payload = valid_booking_payload(guests=0)
    response = await client.post('/api/v1/bookings/', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_booking_invalid_guests_too_many(client):
    """Проверяет, что при количестве гостей больше 12 возвращается 422."""
    payload = valid_booking_payload(guests=13)
    response = await client.post('/api/v1/bookings/', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_booking_conflict(client):
    """Проверяет, что при повторной брони на занятый слот возвращается 409."""
    payload = valid_booking_payload()
    # Первая бронь
    response1 = await client.post('/api/v1/bookings/', json=payload)
    assert response1.status_code == 201
    # Вторая бронь на тот же слот
    response2 = await client.post('/api/v1/bookings/', json=payload)
    assert response2.status_code == 409
    assert response2.json()['detail'] == 'Слот уже занят'


# -----Тесты на получение списка-----
@pytest.mark.asyncio
async def test_get_bookings_empty(client):
    """Проверяет, что при отсутствии броней список пуст."""
    response = await client.get('/api/v1/bookings/')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_bookings_with_filter(client):
    """Проверяет фильтрацию списка броней по дате."""
    tomorrow = date.today() + timedelta(days=1)
    day_after = date.today() + timedelta(days=2)

    payload1 = valid_booking_payload(booking_date=str(tomorrow), booking_time='14:00')
    payload2 = valid_booking_payload(booking_date=str(day_after), booking_time='15:00')

    await client.post('/api/v1/bookings/', json=payload1)
    await client.post('/api/v1/bookings/', json=payload2)

    response = await client.get(f'/api/v1/bookings/?date={tomorrow}')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['booking_date'] == str(tomorrow)


# -----Тесты на получение одной брони-----
@pytest.mark.asyncio
async def test_get_booking_by_id_success(client):
    """Проверяет получение брони по id."""
    payload = valid_booking_payload()
    create_resp = await client.post('/api/v1/bookings/', json=payload)
    booking_id = create_resp.json()['id']

    response = await client.get(f'/api/v1/bookings/{booking_id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == booking_id
    assert data['name'] == payload['name']


@pytest.mark.asyncio
async def test_get_booking_not_found(client):
    """Проверяет, что запрос несуществующей брони возвращает 404."""
    response = await client.get('/api/v1/bookings/999/')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Booking not found'


# -----Тесты на отмену брони-----
@pytest.mark.asyncio
async def test_cancel_booking_success(client):
    """Проверяет успешную отмену брони и освобождение слота."""
    payload = valid_booking_payload()
    create_resp = await client.post('/api/v1/bookings/', json=payload)
    booking_id = create_resp.json()['id']

    cancel_resp = await client.delete(f'/api/v1/bookings/{booking_id}/')
    assert cancel_resp.status_code == 200
    data = cancel_resp.json()
    assert data['id'] == booking_id
    assert data['status'] == 'cancelled'

    new_booking_resp = await client.post('/api/v1/bookings/', json=payload)
    assert new_booking_resp.status_code == 201


@pytest.mark.asyncio
async def test_cancel_booking_not_found(client):
    """Проверяет, что отмена несуществующей брони возвращает 404."""
    response = await client.delete('/api/v1/bookings/999/')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Booking not found'