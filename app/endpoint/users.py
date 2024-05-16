from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.requests import Request

from app.core.dependencies import get_user_id_by_token
from app.core.redis_client import Redis
from app.core.security import get_hashed_psw, authenticate_user, create_access_token, create_refresh_token, decode_jwt, \
    is_access_token, is_set_password_token, generate_salt, get_password_hash, verify_password, \
    get_changed_hashed_password
from app.db.CRUD import BaseCRUD
from app.processes.processes import send_verify_email, send_email_new_ip
from app.schemas.seller import SManagerSetPassword
from app.schemas.user import SUserSignUp, SToken, STokenResponse, SOkResponse, SPasswordChange, STokenVerify, UserLogIn
from app.core.config import settings

users = APIRouter(
    prefix="/api/v1/auth",
    tags=['Authentication and Authorization'],
)


@users.post('/register', status_code=201)
async def registration(param: Annotated[SUserSignUp, Depends()], request: Request) -> SOkResponse:
    user = await get_hashed_psw(param, request.client.host)
    user_id = await BaseCRUD.add_user(user)
    send_verify_email.delay(user_id=user_id, email=param.email)
    return SOkResponse()


@users.post('/login')
async def get_token(param: Annotated[UserLogIn, Depends()],
                    response: Response, request: Request) -> STokenResponse:
    user = await authenticate_user(email=param.username, password=param.password)
    if request.client.host not in user.white_list_ip:
        send_email_new_ip.delay(user_id=user.id, email=user.email, request_ip=request.client.host)
    payload = {'sub': user.id, 'role': user.role, 'username': user.email, 'is_active': user.is_active,
               'is_enabled': user.is_enabled, 'is_admin': user.is_admin, 'is_baned': user.is_baned}
    access_token = create_access_token(data=payload)
    refresh_token = create_refresh_token(data=payload)
    response.set_cookie(key='access_token', value=access_token,
                        expires=60 * settings.auth_jwt.access_token_expire_minutes)
    await Redis.set(request.client.host, refresh_token, 60 * 60 * 24 * settings.auth_jwt.refresh_token_expire_days)
    return STokenResponse(data=SToken(access_token=access_token))


@users.post('/refresh')
async def auth_refresh_jwt(request: Request, response: Response) -> STokenResponse:
    payload = decode_jwt(token=await Redis.get(request.client.host))
    if payload.get('type') == 'access':
        raise HTTPException(
            status_code=403,
            detail='Incorrect refresh token'
        )

    refresh_token = create_refresh_token(data=payload)
    payload.update({'type': 'access'})
    access_token = create_access_token(data=payload)

    response.set_cookie(key='access_token', value=access_token)
    await Redis.set(request.client.host, refresh_token, 60 * 60 * 24 * settings.auth_jwt.refresh_token_expire_days)
    return STokenResponse(data=SToken(access_token=access_token))


@users.post('/logout')
async def logout_user(response: Response, request: Request) -> SOkResponse:
    response.delete_cookie('access_token')
    await Redis.delete(request.client.host)
    return SOkResponse()


@users.post('/delete_account')
async def delete_account(user_id: Annotated[int, Depends(get_user_id_by_token)],
                         request: Request, response: Response) -> SOkResponse:
    await BaseCRUD.deactivate_account(user_id)
    await Redis.delete(request.client.host)
    response.delete_cookie('access_token')
    return SOkResponse()


@users.post('/token')
async def set_password_by_manager(param: Annotated[SManagerSetPassword, Depends()]) -> SOkResponse:
    payload = is_set_password_token(token=param.token)
    user_id = payload.get('sub')
    salt = generate_salt()
    hashed_password = get_password_hash(password=param.password + salt)
    await BaseCRUD.set_password_by_manager(user_id=user_id, hashed_password=hashed_password, salt=salt)
    return SOkResponse()


@users.post('/password')
async def change_password(param: Annotated[SPasswordChange, Depends()],
                          user_id: Annotated[int, Depends(get_user_id_by_token)],
                          response: Response, request: Request) -> SOkResponse:

    user = await BaseCRUD.get_user_by_token_id(user_id=user_id)
    if not verify_password(plain_password=param.current_password + user.salt + settings.password_salt.salt_static,
                           hashed_password=user.hashed_password):
        raise HTTPException(
            status_code=403,
            detail='Current password incorrect'
        )
    param = get_changed_hashed_password(new_password=param.new_password)
    await BaseCRUD.update_password(user_id=user_id, param=param)

    payload = {'sub': user.id, 'role': user.role, 'username': user.email, 'is_active': user.is_active,
               'is_enabled': user.is_enabled, 'is_admin': user.is_admin, 'is_baned': user.is_baned}
    access_token = create_access_token(data=payload)
    refresh_token = create_refresh_token(data=payload)
    response.set_cookie(key='access_token', value=access_token,
                        expires=60 * settings.auth_jwt.access_token_expire_minutes)
    await Redis.set(request.client.host, refresh_token, 60 * 60 * 24 * settings.auth_jwt.refresh_token_expire_days)

    return SOkResponse()


@users.post('/email')
async def verify_user_email(param: Annotated[STokenVerify, Depends()]) -> SOkResponse:
    payload = is_set_password_token(token=param.token)
    user_id = payload.get('sub')
    await BaseCRUD.verify_email(user_id=user_id)
    return SOkResponse()


# TODO
# Просмотр контактной информации о компании/продавце/пользователе админами
# Добавить суперадминов, которые могут назначать адинов
# Добавление владельцами компаний менеджеров и др. для с ограниченными правами доступа к кабинету компании
# Вывод списка товаров с фильтрами
