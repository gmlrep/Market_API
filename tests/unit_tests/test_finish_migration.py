import pytest
from unittest.mock import AsyncMock, patch

from app.processes.email_templates import (
    get_email_template_verify,
    get_email_template_new_ip,
)
from app.schemas.customer import SReviewAdd
from app.schemas.seller import SManagerSignUp
from app.core.security import decode_jwt, create_img
from app.core.exceptions import UnauthorizedError, ForbiddenError, NotFoundError, AuthError


def test_email_verify_sub_is_string():
    msg = get_email_template_verify(user_id=42, email_addr="a@b.com")
    # extract token from HTML body
    body = msg.get_content()
    assert "token/" in body
    token = body.split("token/")[1].split("<")[0].strip()
    payload = decode_jwt(token)
    assert payload["sub"] == "42"
    assert isinstance(payload["sub"], str)


def test_email_new_ip_template():
    msg = get_email_template_new_ip(email_addr="a@b.com", request_ip="1.2.3.4")
    assert "1.2.3.4" in msg.get_content()


@pytest.mark.asyncio
async def test_redis_connect_with_password():
    from app.core import redis_client

    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    mock_client.aclose = AsyncMock()

    with (
        patch("app.core.redis_client.settings") as mock_settings,
        patch("app.core.redis_client.redis.StrictRedis", return_value=mock_client) as ctor,
    ):
        mock_settings.redis_settings.host = "localhost"
        mock_settings.redis_settings.port = 6379
        mock_settings.redis_settings.password = "secret"
        await redis_client.Redis.connect()
        kwargs = ctor.call_args.kwargs
        assert kwargs["password"] == "secret"
        await redis_client.Redis.close()


@pytest.mark.asyncio
async def test_add_review_success(container):
    service = container.customer_service()
    review_id = await service.add_review(
        data=SReviewAdd(product_id=1, rate=5, comment="great"),
        user_id=1,
    )
    assert review_id > 0


@pytest.mark.asyncio
async def test_add_manager(container):
    service = container.seller_service()
    seller_id = await service.add_manager(
        user_id=2,
        param=SManagerSignUp(email="manager@test.com", fullname="Mgr", age=28),
    )
    assert seller_id > 0


def test_exception_status_codes():
    assert UnauthorizedError(detail="x").status_code == 401
    assert ForbiddenError(detail="x").status_code == 406
    assert NotFoundError(detail="x").status_code == 404
    assert AuthError(detail="x").status_code == 403


def test_create_img(tmp_path, monkeypatch):
    from io import BytesIO
    from PIL import Image

    media = tmp_path / "media" / "users"
    media.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    buf = BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="JPEG")
    buf.seek(0)

    class FakeUpload:
        def __init__(self):
            self.file = buf

    create_img(user_id=1, files=[FakeUpload()], source="users")
    assert (tmp_path / "media" / "users" / "users1_1.jpg").exists()


@pytest.mark.asyncio
async def test_seller_manager_endpoint(client, seller_cookies):
    client.cookies.set("access_token", seller_cookies["access_token"])
    response = await client.post(
        "/api/v1/sellers/manager",
        params={"email": "mgr2@test.com", "fullname": "Manager Two", "age": 30},
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_redis_url_helpers():
    from app.core.config import settings

    url = settings.redis_settings.redis_url
    assert url.startswith("redis://")
    assert settings.redis_settings.broker_url == url
