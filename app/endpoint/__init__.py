"""Compatibility re-exports — prefer app.api.v1.endpoints."""

from app.api.v1.endpoints.auth import users  # noqa: F401
from app.api.v1.endpoints.customers import customers  # noqa: F401
from app.api.v1.endpoints.sellers import sellers  # noqa: F401
