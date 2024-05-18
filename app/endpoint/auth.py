from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.requests import Request

from app.core.dependencies import get_user_id_by_token, get_user_id_by_set_token
from app.core.redis_client import Redis
from app.core.security import get_hashed_psw, authenticate_user, decode_jwt, \
    is_set_password_token, generate_salt, get_password_hash, verify_password, \
    get_changed_hashed_password, set_update_tokens
from app.processes.processes import send_verify_email, send_email_new_ip
from app.schemas.seller import SManagerSetPassword
from app.schemas.user import SToken, STokenResponse, SOkResponse, SPasswordChange, UserLogIn
from app.core.config import settings
from app.services.users import UsersService

users = APIRouter(
    prefix="/api/v1/auth",
    tags=['Auth'],
)


@users.post('/register', status_code=201)
async def registration(user=Depends(get_hashed_psw)) -> SOkResponse:
    user_id = await UsersService().add_one(user)
    send_verify_email.delay(user_id=user_id, email=user.email)
    return SOkResponse()


@users.post('/login')
async def get_token(param: Annotated[UserLogIn, Depends()],
                    response: Response, request: Request) -> STokenResponse:
    user = await authenticate_user(email=param.username, password=param.password)
    if request.client.host not in user.white_list_ip:
        send_email_new_ip.delay(user_id=user.id, email=user.email, request_ip=request.client.host)
    access_token = await set_update_tokens(user=user, request=request, response=response)
    return STokenResponse(data=SToken(access_token=access_token))


@users.post('/refresh')
async def auth_refresh_jwt(request: Request, response: Response,
                           user_id: Annotated[int, Depends(get_user_id_by_token)]) -> STokenResponse:
    payload = decode_jwt(token=await Redis.get(request.client.host))
    if payload.get('type') == 'access':
        raise HTTPException(
            status_code=403,
            detail='Incorrect refresh token'
        )
    user = await UsersService().find_one(filter_by={'id': user_id})
    access_token = await set_update_tokens(user=user, request=request, response=response)
    return STokenResponse(data=SToken(access_token=access_token))


@users.post('/logout')
async def logout_user(response: Response, request: Request) -> SOkResponse:
    response.delete_cookie('access_token')
    await Redis.delete(request.client.host)
    return SOkResponse()


@users.post('/delete_account')
async def delete_account(user_id: Annotated[int, Depends(get_user_id_by_token)],
                         request: Request, response: Response) -> SOkResponse:
    await UsersService().update(filter_by={'id': user_id}, update_value={'is_active': False})
    await Redis.delete(request.client.host)
    response.delete_cookie('access_token')
    return SOkResponse()


@users.post('/token')
async def set_password_by_manager(param: Annotated[SManagerSetPassword, Depends()],
                                  user_id: Annotated[int, Depends(get_user_id_by_set_token)]) -> SOkResponse:
    salt = generate_salt()
    hashed_password = get_password_hash(password=param.password + salt)
    await UsersService().update(filter_by={'id': user_id},
                                update_value={'hashed_password': hashed_password, 'salt': salt,
                                              'is_active': True, 'is_enabled': True})
    return SOkResponse()


@users.post('/password')
async def change_password(param: Annotated[SPasswordChange, Depends()],
                          user_id: Annotated[int, Depends(get_user_id_by_token)],
                          response: Response, request: Request) -> SOkResponse:
    user = await UsersService().find_one(filter_by={'id': user_id})
    if not verify_password(plain_password=param.current_password + user.salt + settings.password_salt.salt_static,
                           hashed_password=user.hashed_password):
        raise HTTPException(
            status_code=403,
            detail='Current password incorrect'
        )
    param = get_changed_hashed_password(new_password=param.new_password)
    await UsersService().update(filter_by={'id': user_id}, update_value=param.model_dump())
    await set_update_tokens(user=user, request=request, response=response)
    return SOkResponse()


@users.post('/email')
async def verify_user_email(user_id: Annotated[int, Depends(get_user_id_by_set_token)]) -> SOkResponse:
    await UsersService().update(filter_by={'id': user_id}, update_value={'is_enabled': True})
    return SOkResponse()


# TODO
# Добавить суперадминов, которые могут назначать адинов
# Добавление владельцами компаний менеджеров и др. с ограниченными правами доступа к кабинету компании
# Вывод списка товаров с фильтрами
# Дописать паттерн репозиторий
