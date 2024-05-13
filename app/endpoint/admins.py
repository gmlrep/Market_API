import shutil
from pprint import pprint
from typing import Annotated

from PIL import Image
from redis import asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Response, Request, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from app.core.redis_client import Redis
from app.core.security import get_hashed_psw, authenticate_user, create_access_token, create_refresh_token, decode_jwt, \
    is_refresh_token, create_img, access_admin
from app.db.CRUD import BaseCRUD
from app.schemas.admin import SCategoryAdd, SUserId
from app.schemas.user import SUserSignUp, SToken, STokenResponse, SOkResponse, SUserEdit
from app.core.config import settings

admins = APIRouter(
    prefix="/api/v1/admin",
    tags=['admins'],
    dependencies=[Depends(access_admin)]
)


@admins.post('/add_category')
async def add_category(param: Annotated[SCategoryAdd, Depends()]) -> SOkResponse:

    await BaseCRUD.add_category(param)
    return SOkResponse()


@admins.post('/ban')
async def ban_user_by_id(param: Annotated[SUserId, Depends()]) -> SOkResponse:
    await BaseCRUD.ban_user(param)
    return SOkResponse()
