import shutil
from pprint import pprint
from typing import Annotated

from PIL import Image
from redis import asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Response, Request, File, UploadFile
from fastapi.requests import Request

from app.core.redis_client import Redis
from app.core.security import get_hashed_psw, authenticate_user, create_access_token, create_refresh_token, decode_jwt, \
    is_refresh_token, create_img, access_customer
from app.db.CRUD import BaseCRUD
from app.schemas.customer import SCategory, SProductsInfo, SProduct, SAccountInfo
from app.schemas.user import SUserSignUp, SToken, STokenResponse, SOkResponse, SUserEdit
from app.core.config import settings

customers = APIRouter(
    prefix="/api/v1/customers",
    tags=['customers'],
    dependencies=[Depends(access_customer)]
)


@customers.post('/edit_profile')
async def edit_profile(param: Annotated[SUserEdit, Depends()], request: Request, file: UploadFile = None) -> SOkResponse:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    await BaseCRUD.edit_profile_user(param=param, user_id=user_id)

    create_img(user_id=user_id, files=file, source='users') if file is not None else ...
    return SOkResponse()


@customers.get('/category/{category}')
async def get_product_by_category(param: Annotated[SCategory, Depends()]) -> list[SProductsInfo]:
    category_id = await Redis.get(param.category)
    products = await BaseCRUD.get_products_category(category_id)
    return products


@customers.get('/product/{product_id}')
async def get_product_by_id(param: Annotated[SProduct, Depends()]) -> SProductsInfo:
    product = await BaseCRUD.get_product_by_product_id(product_id=param.product_id)
    return product


@customers.get('/account')
async def get_account_info(request: Request) -> SAccountInfo:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    user = await BaseCRUD.get_account_info(user_id=user_id)
    return user

