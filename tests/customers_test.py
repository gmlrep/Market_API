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


async def test_get_products_by_category(authenticated_customer_ac: AsyncClient):
    response = await authenticated_customer_ac.get('api/v1/customers/category/category1', params={
        'page': 1,
    })
    assert response.json()[0]['name'] == 'product1'
    assert response.status_code == 200


async def test_get_products_by_id(authenticated_customer_ac: AsyncClient):
    response = await authenticated_customer_ac.get('api/v1/customers/product/1')
    assert response.json()['name'] == 'product1'
    assert response.status_code == 200


@pytest.mark.parametrize('product_id, quantity, status_code', [
    (1, 1, 201),

    # Некорректное выполнение, создает ордер с несуществующим product_id
    # (2, 1, 201),

    (1, -1, 422),
    ('string', 1, 422),
])
async def test_add_basket(product_id, quantity, status_code, authenticated_customer_ac: AsyncClient):
    response = await authenticated_customer_ac.post('api/v1/customers/basket', params={
        'product_id': product_id,
        'quantity': quantity,
    })
    assert response.status_code == status_code


@pytest.mark.parametrize('city, street, house, building, literal, apartment, status_code', [
    ('big_city', 'some_name_street', 23, 34, 'A', 45, 201),
    ('big_city', 'some_name_street', 23, 34, 'A', 45, 403),
])
async def test_add_contact(city, street, house, building, literal,
                           apartment, status_code, authenticated_customer_ac: AsyncClient):
    params = {
        'city': city,
        'street': street,
        'house': house,
        'building': building,
        'literal': literal,
        'apartment': apartment,
    }
    params = {i: params[i] for i in params if params[i]}
    response = await authenticated_customer_ac.post('api/v1/customers/contact', params=params)
    assert response.status_code == status_code


@pytest.mark.parametrize('city, street, house, building, literal, apartment, status_code', [
    ('new_big_city', 'some_new_name_street', 567, None, 'A', None, 200),
])
async def test_edit_contact(city, street, house, building, literal,
                            apartment, status_code, authenticated_customer_ac: AsyncClient):
    params = {
        'city': city,
        'street': street,
        'house': house,
        'building': building,
        'literal': literal,
        'apartment': apartment,
    }
    params = {i: params[i] for i in params if params[i]}
    response = await authenticated_customer_ac.put('api/v1/customers/contact', params=params)
    assert response.status_code == status_code
