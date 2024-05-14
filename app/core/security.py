import random
import re
import shutil

import jwt

from datetime import datetime, timedelta

from PIL import Image
from fastapi import HTTPException
from passlib.context import CryptContext

from app.core.config import settings
from app.db.CRUD import BaseCRUD
from app.schemas.user import SUserSignUp, SUserAdd, SUserInfo

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


def is_refresh_token(token: str) -> dict:
    payload = decode_jwt(token)
    if payload.get('type') == 'refresh':
        raise HTTPException(
            status_code=401,
            detail="Expected 'access token' and got 'refresh token'",
        )
    return payload


def generate_salt() -> str:
    letters_list = 'abcdefghijklmnopqstyvwxyz1234567890'
    salt_list = [random.choice(letters_list) for i in range(10)]
    salt = ''.join(salt_list)
    return salt


async def get_hashed_psw(param: SUserSignUp, current_ip: str = None) -> SUserAdd:
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
        white_list_ip=current_ip
    )


async def authenticate_user(email: str, password: str) -> SUserInfo | bool:
    user = await BaseCRUD.get_user(email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(plain_password=password + user.salt + settings.password_salt.salt_static,
                           hashed_password=user.hashed_password):
        return False
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
