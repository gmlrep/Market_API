import pytest


@pytest.mark.asyncio
async def test_categories_requires_auth(client):
    response = await client.get("/api/v1/customers/category")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_categories(client, customer_cookies):
    client.cookies.set("access_token", customer_cookies["access_token"])
    response = await client.get("/api/v1/customers/category")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_product(client, customer_cookies):
    client.cookies.set("access_token", customer_cookies["access_token"])
    response = await client.get("/api/v1/customers/product/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"


@pytest.mark.asyncio
async def test_get_products_by_category(client, customer_cookies):
    client.cookies.set("access_token", customer_cookies["access_token"])
    response = await client.get("/api/v1/customers/category/category1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_account_info(client, customer_cookies):
    client.cookies.set("access_token", customer_cookies["access_token"])
    response = await client.get("/api/v1/customers/account")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_seller_forbidden_for_customer(client, customer_cookies):
    client.cookies.set("access_token", customer_cookies["access_token"])
    response = await client.post(
        "/api/v1/sellers/company",
        params={"type_company": 1, "name": "X"},
    )
    assert response.status_code == 406
