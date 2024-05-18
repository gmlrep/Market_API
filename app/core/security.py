import random
import re
import shutil
from typing import Annotated

import jwt

from datetime import datetime, timedelta

from PIL import Image
from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from fastapi import Request
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.redis_client import Redis
from app.db.CRUD import BaseCRUD
from app.schemas.customer import SPage, SPagination
from app.schemas.seller import SManagerSignUp, SManagerAdd
from app.schemas.user import SUserSignUp, SUserAdd, SUserInfo, HashedPasswordSalt
from app.services.users import UsersService

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password + settings.password_salt.salt_static)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def encode_jwt(payload: dict, expires_delta: timedelta) -> str:
    to_encode = payload.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    try:
        token = jwt.encode(
            to_encode,
            key=settings.auth_jwt.private_key_path.read_text(),
            algorithm=settings.auth_jwt.algorithm
        )
        return token
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail='Invalid private key'
        )


def decode_jwt(token: str) -> dict:
    try:
        jwt_decode = jwt.decode(
            token,
            key=settings.auth_jwt.public_key_path.read_text(),
            algorithms=settings.auth_jwt.algorithm)
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
        raise HTTPException(
            status_code=403,
            detail='Incorrect token'
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=403,
            detail='Access token has expired'
        )
    return jwt_decode


def is_access_token(token: str) -> dict:
    payload = decode_jwt(token)
    if payload.get('type') != 'access':
        raise HTTPException(
            status_code=401,
            detail="Expected 'access token' and got 'refresh token'",
        )
    return payload


def is_set_password_token(token: str) -> dict:
    payload = decode_jwt(token)
    if payload.get('type') != 'set_password':
        raise HTTPException(
            status_code=401,
            detail="Incorrect token",
        )
    return payload


def generate_salt() -> str:
    letters_list = 'abcdefghijklmnopqstyvwxyz1234567890'
    salt_list = [random.choice(letters_list) for i in range(10)]
    salt = ''.join(salt_list)
    return salt


async def get_hashed_psw(param: Annotated[SUserSignUp, Depends()], request: Request) -> SUserAdd:
    salt = generate_salt()
    regex = "^[a-zA-Z0-9?.,*+_()&%=$#!]+$"
    pattern = re.compile(regex)
    if pattern.search(param.password) is None:
        raise HTTPException(
            status_code=403,
            detail='Unsupported letters, only english letters, numbers and special symbols'
        )

    hashed_password = get_password_hash(password=param.password + salt)
    return SUserAdd(
        fullname=param.fullname,
        role=param.role,
        age=param.age,
        email=param.email,
        hashed_password=hashed_password,
        salt=salt,
        white_list_ip=request.client.host
    )


def get_changed_hashed_password(new_password: str):
    salt = generate_salt()
    regex = "^[a-zA-Z0-9?.,*+_()&%=$#!]+$"
    pattern = re.compile(regex)
    if pattern.search(new_password) is None:
        raise HTTPException(
            status_code=403,
            detail='Unsupported letters, only english letters, numbers and special symbols'
        )
    hashed_password = get_password_hash(password=new_password + salt)
    return HashedPasswordSalt(hashed_password=hashed_password, salt=salt)


async def get_manager_to_add(param: SManagerSignUp, current_ip: str = '34') -> SManagerAdd:
    salt = generate_salt()
    password = generate_salt()

    hashed_password = get_password_hash(password=password + salt)
    return SManagerAdd(
        fullname=param.fullname,
        role=2,
        age=param.age,
        email=param.email,
        hashed_password=hashed_password,
        salt=salt,
        white_list_ip=current_ip
    )


async def authenticate_user(email: str, password: str) -> SUserInfo | bool:
    user = await UsersService().find_one({'email': email})
    # user = await BaseCRUD.get_user(email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(plain_password=password + user.salt + settings.password_salt.salt_static,
                           hashed_password=user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password'
        )
    return user


def create_jwt(token_data: dict, token_type, expires_delta: timedelta) -> str:
    jwt_payload = {'type': token_type}
    jwt_payload.update(token_data)
    return encode_jwt(payload=jwt_payload, expires_delta=expires_delta)


def create_access_token(data: dict) -> str:
    expire_delta = timedelta(minutes=settings.auth_jwt.access_token_expire_minutes)
    return create_jwt(
        token_data=data,
        token_type='access',
        expires_delta=expire_delta
    )


def create_refresh_token(data: dict) -> str:
    expire_delta = timedelta(days=settings.auth_jwt.refresh_token_expire_days)
    return create_jwt(
        token_data=data,
        token_type='refresh',
        expires_delta=expire_delta
    )


def pagination_param(page: Annotated[SPage, Depends()]):
    per_page = settings.page_limit
    start = (page.page - 1) * per_page
    end = start + per_page
    return SPagination(start=start, end=end)


def is_valid_token(token: str) -> bool:
    try:
        payload = jwt.decode(
            token,
            key=settings.auth_jwt.public_key_path.read_text(),
            algorithms=settings.auth_jwt.algorithm)
        if payload.get('type') == 'refresh':
            return False
        return True
    except:
        return False


def create_img(user_id: int, files, source: str):
    for i, file in enumerate(files):
        with open(f'media/{source}/{source}{user_id}_{i + 1}.jpg', 'wb+') as buffer:
            shutil.copyfileobj(file.file, buffer)

        with Image.open(f'media/{source}/{source}{user_id}_{i + 1}.jpg') as photo:
            if photo.mode in ('RGBA', 'P'):
                photo = photo.convert('RGB')
            photo.save(f'media/{source}/{source}{user_id}_{i + 1}.jpg', 'JPEG', quality=20)


async def is_access_token_admin(token: str, request: Request) -> dict:
    try:
        payload = jwt.decode(
            token,
            key=settings.auth_jwt.public_key_path.read_text(),
            algorithms=settings.auth_jwt.algorithm)
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
        raise HTTPException(
            status_code=403,
            detail='Incorrect token'
        )
    except jwt.exceptions.ExpiredSignatureError:
        payload = decode_jwt(token=await Redis.get(request.client.host))
        if payload.get('type') != 'refresh':
            raise HTTPException(
                status_code=403,
                detail='Incorrect refresh token'
            )
        refresh_token = create_refresh_token(data=payload)
        payload.update({'type': 'access'})
        access_token = create_access_token(data=payload)
        request.session.update({'access_token': access_token, 'token_type': 'Bearer'})
        await Redis.set(request.client.host, refresh_token, 60 * 60 * 24 * settings.auth_jwt.refresh_token_expire_days)
    if payload.get('type') != 'access':
        raise HTTPException(
            status_code=401,
            detail="Expected 'access token' and got 'refresh token'",
        )
    return payload


async def set_update_tokens(user, request: Request, response: Response):

    payload = {'sub': user.id, 'role': user.role, 'username': user.email, 'is_active': user.is_active,
               'is_enabled': user.is_enabled, 'is_admin': user.is_admin, 'is_baned': user.is_baned}
    access_token = create_access_token(data=payload)
    refresh_token = create_refresh_token(data=payload)
    response.set_cookie(key='access_token', value=access_token,
                        expires=60 * settings.auth_jwt.access_token_expire_minutes)
    await Redis.set(request.client.host, refresh_token, 60 * 60 * 24 * settings.auth_jwt.refresh_token_expire_days)
    return access_token
