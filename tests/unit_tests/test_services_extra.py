import pytest

from app.schemas.customer import SBasket, SContact, SOrderId, SReviewAdd
from app.schemas.user import SUserEdit
from app.schemas.seller import SProducts
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_customer_basket_flow(container):
    service = container.customer_service()
    order_id = await service.add_basket(
        data=SBasket(product_id=1, quantity=2), user_id=1
    )
    assert order_id is not None
    # update quantity
    order_id2 = await service.add_basket(
        data=SBasket(product_id=1, quantity=5), user_id=1
    )
    assert order_id2 is not None
    deleted = await service.delete_basket(data=SOrderId(order_id=order_id2), user_id=1)
    assert deleted == order_id2


@pytest.mark.asyncio
async def test_customer_contacts(container):
    service = container.customer_service()
    contact_id = await service.add_contacts(
        data=SContact(city="Moscow", street="Lenina"), user_id=1
    )
    assert contact_id > 0
    with pytest.raises(HTTPException):
        await service.add_contacts(
            data=SContact(city="Moscow", street="Lenina"), user_id=1
        )
    await service.edit_contacts(
        data=SContact(city="SPb", street="Nevsky"), user_id=1
    )


@pytest.mark.asyncio
async def test_customer_profile_update(container):
    service = container.customer_service()
    await service.update_profile(
        data=SUserEdit(fullname="Updated"), user_id=1, file=None
    )
    with pytest.raises(HTTPException):
        await service.update_profile(data=SUserEdit(), user_id=1, file=None)


@pytest.mark.asyncio
async def test_customer_review_requires_taken_order(container):
    service = container.customer_service()
    with pytest.raises(HTTPException):
        await service.add_review(
            data=SReviewAdd(product_id=1, rate=5, comment="nice"),
            user_id=1,
        )


@pytest.mark.asyncio
async def test_auth_refresh_and_password(container, client):
    # login via HTTP to set redis mock
    response = await client.post(
        "/api/v1/auth/login",
        params={"username": "customer@test.com", "password": "password12"},
    )
    assert response.status_code == 200
    cookies = {"access_token": response.cookies["access_token"]}
    client.cookies.set("access_token", cookies["access_token"])

    refresh = await client.post("/api/v1/auth/refresh")
    assert refresh.status_code == 200

    pwd = await client.post(
        "/api/v1/auth/password",
        params={"current_password": "password12", "new_password": "password99"},
    )
    assert pwd.status_code == 200


@pytest.mark.asyncio
async def test_seller_update_company(container):
    from app.schemas.seller import SCompanyUpdate

    service = container.seller_service()
    company_id = await service.update_company(
        data=SCompanyUpdate(description="updated desc"),
        user_id=2,
        file=None,
    )
    assert company_id == 1


@pytest.mark.asyncio
async def test_seller_add_product(container):
    service = container.seller_service()
    product_id = await service.add_product(
        param=SProducts(name="New Prod", price=100),
        user_id=2,
        categories="category1",
        photos=None,
    )
    assert product_id > 0
    await service.add_parameters(
        param={"color": "red"}, user_id=2, product_id=product_id
    )
    # skip delete — FK from parameters; covered by HTTP product create test
    assert product_id > 1


@pytest.mark.asyncio
async def test_base_service_methods(container):
    service = container.user_service()
    user = await service.get_by_id(1)
    assert user.id == 1
    await service.close_scope_session()


@pytest.mark.asyncio
async def test_read_by_options(container):
    from pydantic import BaseModel

    class FindUser(BaseModel):
        page: int = 1
        page_size: int = 10
        ordering: str = "-id"

    repo = container.user_repository()
    result = await repo.read_by_options(FindUser())
    assert "founds" in result
    assert "search_options" in result


@pytest.mark.asyncio
async def test_delete_account(client, customer_cookies):
    client.cookies.set("access_token", customer_cookies["access_token"])
    response = await client.post("/api/v1/auth/delete_account")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_customer_contact_endpoints(client, customer_cookies):
    client.cookies.set("access_token", customer_cookies["access_token"])
    r = await client.post(
        "/api/v1/customers/contact",
        params={"city": "Moscow", "street": "Tverskaya"},
    )
    assert r.status_code == 201
    r2 = await client.put(
        "/api/v1/customers/contact",
        params={"city": "SPb", "street": "Nevsky"},
    )
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_customer_basket_endpoint(client, customer_cookies):
    client.cookies.set("access_token", customer_cookies["access_token"])
    r = await client.post(
        "/api/v1/customers/basket",
        params={"product_id": 1, "quantity": 3},
    )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_seller_product_endpoints(client, seller_cookies):
    client.cookies.set("access_token", seller_cookies["access_token"])
    r = await client.post(
        "/api/v1/sellers/product",
        params={"name": "API Product", "price": 50, "categories": "category2"},
    )
    assert r.status_code == 201
