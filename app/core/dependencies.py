from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import Depends
from fastapi.requests import Request

from app.core.container import Container
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.middleware.inject import inject
from app.core.security import is_access_token, is_set_password_token
from app.schemas.seller import SToken
from app.schemas.user import SUserInfo
from app.services.users import UsersService


def _require_access_payload(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if token is None:
        raise UnauthorizedError(detail="Not authorized")
    return is_access_token(token=token)


def access_admin(request: Request):
    payload = _require_access_payload(request)
    if not payload.get("is_admin"):
        raise ForbiddenError(detail="Do not permission")


def access_seller(request: Request):
    payload = _require_access_payload(request)
    if payload.get("role") != 2:
        raise ForbiddenError(detail="Do not permission")


def access_customer(request: Request):
    payload = _require_access_payload(request)
    if payload.get("role") != 1:
        raise ForbiddenError(detail="Do not permission")


def get_user_id_by_token(request: Request) -> int:
    payload = _require_access_payload(request)
    return int(payload.get("sub"))


def get_user_id_by_set_token(token: Annotated[SToken, Depends()]) -> int:
    payload = is_set_password_token(token=token.token)
    return int(payload.get("sub"))


@inject
async def get_current_user(
    request: Request,
    user_service: Annotated[UsersService, Depends(Provide[Container.user_service])],
) -> SUserInfo:
    user_id = get_user_id_by_token(request)
    user = await user_service.find_one(filter_by={"id": user_id})
    if not user:
        raise UnauthorizedError(detail="User not found")
    return user
