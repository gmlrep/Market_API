import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt,
    is_access_token,
    generate_salt,
    get_password_hash,
    verify_password,
)
from app.core.config import settings
from app.core.exceptions import NotFoundError, DuplicateError, AuthError


def test_generate_salt():
    salt = generate_salt()
    assert len(salt) == 10


def test_password_hash_verify():
    salt = "abcdef1234"
    password = "password12"
    hashed = get_password_hash(password + salt)
    assert verify_password(
        plain_password=password + salt + settings.password_salt.salt_static,
        hashed_password=hashed,
    )


def test_jwt_access_roundtrip():
    token = create_access_token(data={"sub": "1", "role": 1})
    payload = is_access_token(token)
    assert payload["sub"] == "1"
    assert payload["type"] == "access"


def test_jwt_refresh_not_access():
    token = create_refresh_token(data={"sub": "1", "role": 1})
    with pytest.raises(Exception):
        is_access_token(token)


def test_decode_invalid_token():
    with pytest.raises(Exception):
        decode_jwt("not.a.token")


def test_exception_classes():
    assert NotFoundError(detail="x").status_code == 404
    assert DuplicateError(detail="x").status_code == 400
    assert AuthError(detail="x").status_code == 403
