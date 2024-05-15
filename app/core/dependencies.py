from fastapi import FastAPI, Depends, HTTPException, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.requests import Request

from app.core.security import decode_jwt, is_access_token


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
