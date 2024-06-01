import pytest

from httpx import AsyncClient


async def test_add_company(authenticated_seller_ac: AsyncClient):
    response = await authenticated_seller_ac.post('api/v1/sellers/company', params={
        'name': 'company_name',
        'type_company': 1,
    })
    assert response.status_code == 201


@pytest.mark.parametrize('name, status_code', [
    ('new_company_name', 200),
])
async def test_edit_company(name, status_code, authenticated_seller_ac: AsyncClient):
    params = {
        'name': name,
    }
    # params = {i: params[i] for i in params if params[i]}
    response = await authenticated_seller_ac.put('api/v1/sellers/company', params=params)
    assert response.status_code == status_code


@pytest.mark.parametrize('name, price, categories, status_code', [
    ('product1', 230, 'category1', 201),
    ('product2', 345, 'category2', 201),
    ('product2', -230, 'category1', 422),
])
async def test_add_product(name, price, categories, status_code, authenticated_seller_ac: AsyncClient):
    response = await authenticated_seller_ac.post('api/v1/sellers/product', params={
        'name': name,
        'price': price,
        'categories': categories,
    })
    assert response.status_code == status_code


async def test_delete_product(authenticated_seller_ac: AsyncClient):
    response = await authenticated_seller_ac.delete('api/v1/sellers/product', params={
        'product_id': 2
    })
    assert response.status_code == 200


@pytest.mark.parametrize('param, product_id, status_code', [
    ({'param1': 'value1', 'param2': 'value2'}, 1, 201),
])
async def test_add_product_parameters(param, product_id, status_code, authenticated_seller_ac: AsyncClient):
    response = await authenticated_seller_ac.post('api/v1/sellers/parameters', json=param, params={
        'product_id': product_id,
    })
    assert response.status_code == status_code
