import asyncio
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

os.environ["ENVIRONMENT"] = "test"
os.environ["ENV"] = "test"
os.environ.setdefault("SALT_STATIC", "test-static-salt")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "1")
os.environ.setdefault("POSTGRES_TEST_DB", "test_market_api")
os.environ.setdefault("FAST_API_PORT", "9000")
os.environ.setdefault("HOST_REDIS", "localhost")
os.environ.setdefault("PORT_REDIS", "6379")

if os.getenv("ENVIRONMENT") not in ["test"]:
    pytest.exit(f"ENVIRONMENT is not test, it is {os.getenv('ENVIRONMENT')}")


def _ensure_jwt_certs() -> None:
    root = Path(__file__).resolve().parent.parent
    certs = root / "certs"
    private = certs / "jwt-private.pem"
    public = certs / "jwt-public.pem"
    if private.exists() and public.exists():
        return
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    certs.mkdir(parents=True, exist_ok=True)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public.write_bytes(
        key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


_ensure_jwt_certs()

from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from fastapi_cache import FastAPICache  # noqa: E402
from fastapi_cache.backends.inmemory import InMemoryBackend  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.security import get_password_hash, generate_salt  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.models import Users, Category, Companies, Sellers, Products, Orders  # noqa: E402
from app.__main__ import AppCreator  # noqa: E402

TEST_DATA_DIR = Path(__file__).parent / "test_data"

# In-memory Redis stand-in for tests
_REDIS_STORE: dict[str, str] = {}


async def _redis_get(key):
    return _REDIS_STORE.get(key)


async def _redis_set(key, value, expire):
    _REDIS_STORE[key] = value
    return True


async def _redis_delete(key):
    _REDIS_STORE.pop(key, None)
    return 1


@pytest.fixture(scope="session")
def event_loop():
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def _ensure_test_database() -> None:
    db_name = settings.db_settings.db_name
    admin_url = (
        f"postgresql://{settings.db_settings.POSTGRES_USER}:"
        f"{settings.db_settings.POSTGRES_PASSWORD}@"
        f"{settings.db_settings.POSTGRES_HOST}:{settings.db_settings.POSTGRES_PORT}/postgres"
    )
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    engine.dispose()


def insert_default_data(conn) -> None:
    users_data = json.loads((TEST_DATA_DIR / "users.json").read_text(encoding="utf-8"))
    for user in users_data:
        salt = user.get("salt") or generate_salt()
        hashed = get_password_hash(user["password"] + salt)
        conn.execute(
            Users.__table__.insert(),
            {
                "id": user["id"],
                "fullname": user["fullname"],
                "email": user["email"],
                "role": user["role"],
                "age": user.get("age"),
                "hashed_password": hashed,
                "salt": salt,
                "white_list_ip": user.get("white_list_ip", "127.0.0.1"),
                "is_active": user.get("is_active", True),
                "is_enabled": user.get("is_enabled", True),
                "is_baned": user.get("is_baned", False),
                "is_admin": user.get("is_admin", False),
            },
        )

    for cat in json.loads((TEST_DATA_DIR / "categories.json").read_text(encoding="utf-8")):
        conn.execute(Category.__table__.insert(), cat)

    for company in json.loads((TEST_DATA_DIR / "companies.json").read_text(encoding="utf-8")):
        conn.execute(Companies.__table__.insert(), company)

    for seller in json.loads((TEST_DATA_DIR / "sellers.json").read_text(encoding="utf-8")):
        conn.execute(Sellers.__table__.insert(), seller)

    for product in json.loads((TEST_DATA_DIR / "products.json").read_text(encoding="utf-8")):
        conn.execute(Products.__table__.insert(), product)

    for order in json.loads((TEST_DATA_DIR / "orders.json").read_text(encoding="utf-8")):
        conn.execute(Orders.__table__.insert(), order)

    for table in ("users", "category", "company", "sellers", "products", "orders"):
        try:
            conn.execute(
                text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
                )
            )
        except Exception:
            pass


def reset_db():
    _ensure_test_database()
    engine = create_engine(settings.db_settings.db_url_sync)
    with engine.begin() as conn:
        if "test" not in settings.db_settings.db_url_sync:
            raise Exception("Not in test environment")
        Base.metadata.drop_all(conn)
        Base.metadata.create_all(conn)
        insert_default_data(conn)
    engine.dispose()
    return engine


@pytest.fixture(autouse=True)
def _patch_redis_and_celery():
    _REDIS_STORE.clear()
    with (
        patch("app.core.redis_client.Redis.get", side_effect=_redis_get),
        patch("app.core.redis_client.Redis.set", side_effect=_redis_set),
        patch("app.core.redis_client.Redis.delete", side_effect=_redis_delete),
        patch("app.core.security.Redis.get", side_effect=_redis_get),
        patch("app.core.security.Redis.set", side_effect=_redis_set),
        patch("app.core.security.Redis.delete", side_effect=_redis_delete),
        patch("app.services.auth.Redis.get", side_effect=_redis_get),
        patch("app.services.auth.Redis.set", side_effect=_redis_set),
        patch("app.services.auth.Redis.delete", side_effect=_redis_delete),
        patch("app.api.v1.endpoints.auth.send_verify_email.delay", return_value=None),
        patch("app.api.v1.endpoints.auth.send_email_new_ip.delay", return_value=None),
        patch("app.api.v1.endpoints.sellers.send_verify_email.delay", return_value=None),
    ):
        yield


@pytest.fixture
async def client():
    reset_db()
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    AppCreator._instances.clear()
    app_creator = AppCreator()
    app = app_creator.app
    await app_creator.db._async_engine.dispose()
    # Rebuild engine after dispose for this event loop
    from app.core.database import Database

    app_creator.db = Database(db_url=settings.db_settings.db_url)
    app_creator.container.db.override(app_creator.db)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False,
    ) as test_client:
        yield test_client
    await app_creator.db._async_engine.dispose()
    AppCreator._instances.clear()


@pytest.fixture
async def container():
    reset_db()
    AppCreator._instances.clear()
    app_creator = AppCreator()
    await app_creator.db._async_engine.dispose()
    from app.core.database import Database

    db = Database(db_url=settings.db_settings.db_url)
    app_creator.container.db.override(db)
    yield app_creator.container
    await db._async_engine.dispose()
    AppCreator._instances.clear()


@pytest.fixture
async def customer_cookies(client):
    response = await client.post(
        "/api/v1/auth/login",
        params={"username": "customer@test.com", "password": "password12"},
    )
    assert response.status_code == 200, response.text
    return {"access_token": response.cookies["access_token"]}


@pytest.fixture
async def seller_cookies(client):
    response = await client.post(
        "/api/v1/auth/login",
        params={"username": "seller@test.com", "password": "password12"},
    )
    assert response.status_code == 200, response.text
    return {"access_token": response.cookies["access_token"]}
