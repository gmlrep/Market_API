from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.requests import Request

from app.core.security import is_access_token, is_set_password_token
from app.schemas.seller import SToken


def access_admin(request: Request):
    if request.cookies.get('access_token') is None:
        raise HTTPException(
            status_code=401,
            detail='Not authorized'
        )
    payload = is_access_token(token=request.cookies.get('access_token'))
    is_admin = payload.get('is_admin')
    if not is_admin:
        raise HTTPException(
            status_code=406,
            detail='Do not permission'
        )


def access_seller(request: Request):
    if request.cookies.get('access_token') is None:
        raise HTTPException(
            status_code=401,
            detail='Not authorized'
        )
    payload = is_access_token(token=request.cookies.get('access_token'))
    role: int = payload.get('role')
    if role != 2:
        raise HTTPException(
            status_code=406,
            detail='Do not permission'
        )


def access_customer(request: Request):
    if request.cookies.get('access_token') is None:
        raise HTTPException(
            status_code=401,
            detail='Not authorized'
        )
    payload = is_access_token(token=request.cookies.get('access_token'))
    role: int = payload.get('role')
    if role != 1:
        raise HTTPException(
            status_code=406,
            detail='Do not permission'
        )


def get_user_id_by_token(request: Request) -> int:
    payload = is_access_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    return user_id


def get_user_id_by_set_token(token: Annotated[SToken, Depends()]) -> int:
    payload = is_set_password_token(token=token.token)
    user_id = payload.get('sub')
    return user_id
