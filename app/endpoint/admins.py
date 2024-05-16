from typing import Annotated

from redis import asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Response, Request, UploadFile

from app.core.redis_client import Redis

from app.core.dependencies import access_admin
from app.db.CRUD import BaseCRUD
from app.schemas.admin import SCategoryAdd, SBanedUser, SCategoryDelete
from app.schemas.user import SOkResponse
from app.core.config import settings

admins = APIRouter(
    prefix="/api/v1/admin",
    tags=['Admins'],
    dependencies=[Depends(access_admin)]
)


@admins.post('/category', status_code=201)
async def add_category(param: Annotated[SCategoryAdd, Depends()]) -> SOkResponse:

    await BaseCRUD.add_category(param)
    return SOkResponse()


@admins.patch('/ban')
async def ban_unban_user_by_id(param: Annotated[SBanedUser, Depends()]) -> SOkResponse:
    await BaseCRUD.ban_unban_user(param)
    return SOkResponse()


@admins.delete('/category')
async def delete_empty_category(param: Annotated[SCategoryDelete, Depends()]) -> SOkResponse:
    await BaseCRUD.delete_category_by_name_or_id(param=param)
    return SOkResponse()
