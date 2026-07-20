import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post(
        "/api/v1/auth/login",
        params={"username": "customer@test.com", "password": "password12"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "access_token" in body["data"]
    assert response.cookies.get("access_token")


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    response = await client.post(
        "/api/v1/auth/login",
        params={"username": "customer@test.com", "password": "wrongpass1"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        params={
            "email": "newuser@test.com",
            "fullname": "New User",
            "age": 22,
            "role": 1,
            "password": "password12",
        },
    )
    assert response.status_code == 201
    assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_logout(client, customer_cookies):
    client.cookies.set("access_token", customer_cookies["access_token"])
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200
