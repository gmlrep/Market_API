import pytest
from httpx import AsyncClient


@pytest.mark.parametrize('email, fullname, age, password, status_code', [
    ('user@user.com', 'user', 31, 'password12', 201),
    ('user.com', 'user', 31, 'password12', 422),
    ('user@user.com', 'user', -31, 'password12', 422),
    ('user1@user.com', 3456, 31, 'password12', 201),
    ('user1@user.com', 3456, 31, {'key': 'value'}, 403),
])
async def test_register_user(email, password, fullname, age, status_code, ac: AsyncClient):
    response = await ac.post('/api/v1/auth/register', params={
        'email': email,
        'fullname': fullname,
        'age': age,
        'password': password,
    })
    assert response.status_code == status_code


@pytest.mark.parametrize('email, fullname, age, password, role, status_code', [
    ('customer1@customer.com', 'customer', 31, 'password12', 2, 201),
])
async def test_register_customer(email, password, fullname, age, status_code, role, ac: AsyncClient):
    response = await ac.post('/api/v1/auth/register', params={
        'email': email,
        'fullname': fullname,
        'age': age,
        'password': password,
        'role': role
    })
    assert response.status_code == status_code
