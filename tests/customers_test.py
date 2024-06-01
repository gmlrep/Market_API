import pytest
from httpx import AsyncClient


async def test_get_user(authenticated_customer_ac: AsyncClient):
    response = await authenticated_customer_ac.get('/api/v1/customers/account')
    assert response.status_code == 200
    assert response.json()['id'] == 1
    assert response.json()['email'] == 'user@user.com'


@pytest.mark.parametrize('fullname, age, status_code', [
    ('new_name', 34, 200),
    ('new_name', -35, 422),
    (None, 34, 200),
    ('name_user', None, 200),
])
async def test_edit_profile(fullname, age, status_code, authenticated_customer_ac: AsyncClient):
    params = {
        'fullname': fullname,
        'age': age,
    }
    params = {i: params[i] for i in params if params[i]}
    response = await authenticated_customer_ac.put('api/v1/customers/profile', params=params)
    assert response.status_code == status_code


async def test_get_categories(authenticated_customer_ac: AsyncClient):
    response = await authenticated_customer_ac.get('api/v1/customers/category')
    assert response.status_code == 200

