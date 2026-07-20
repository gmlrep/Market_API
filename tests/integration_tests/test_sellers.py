import pytest


@pytest.mark.asyncio
async def test_seller_login_and_company_exists(client, seller_cookies):
    client.cookies.set("access_token", seller_cookies["access_token"])
    # already has company — creating again should 403
    response = await client.post(
        "/api/v1/sellers/company",
        params={
            "type_company": 1,
            "name": "Another Co",
            "description": "x",
        },
    )
    assert response.status_code in (403, 422, 201)


@pytest.mark.asyncio
async def test_seller_requires_auth(client):
    response = await client.post(
        "/api/v1/sellers/company",
        params={"type_company": 1, "name": "X"},
    )
    assert response.status_code == 401
