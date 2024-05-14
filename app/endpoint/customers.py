import shutil
from pprint import pprint
from typing import Annotated

from PIL import Image
from redis import asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Response, File, UploadFile
from fastapi.requests import Request

from app.core.redis_client import Redis
from app.core.security import get_hashed_psw, authenticate_user, create_access_token, create_refresh_token, decode_jwt, \
    is_refresh_token, create_img
from app.core.dependencies import access_customer, get_user_id_by_token
from app.db.CRUD import BaseCRUD
from app.schemas.customer import SCategory, SProductsInfo, SProduct, SAccountInfo, SCategories, SBasket, SOrderId
from app.schemas.user import SUserSignUp, SToken, STokenResponse, SOkResponse, SUserEdit
from app.core.config import settings

customers = APIRouter(
    prefix="/api/v1/customers",
    tags=['customers'],
    dependencies=[Depends(access_customer)]
)


@customers.put('/edit_profile')
async def edit_profile(param: Annotated[SUserEdit, Depends()],
                       user_id: Annotated[int, Depends(get_user_id_by_token)],
                       file: UploadFile = None) -> SOkResponse:

    await BaseCRUD.edit_profile_user(param=param, user_id=user_id, file=file)
    create_img(user_id=user_id, files=file, source='users') if file is not None else ...
    return SOkResponse()


# Обернуть в кэш
@customers.get('/category/{category}')
async def get_product_by_category(param: Annotated[SCategory, Depends()]) -> list[SProductsInfo]:
    products = await BaseCRUD.get_products_category(category_name=param.category)
    return products


@customers.get('/product/{product_id}')
async def get_product_by_id(param: Annotated[SProduct, Depends()]) -> SProductsInfo:
    product = await BaseCRUD.get_product_by_product_id(product_id=param.product_id)
    return product


# Обернуть в кэш
@customers.get('/category_list')
async def get_category_list() -> list[SCategories]:
    categories = await BaseCRUD.get_categories()
    return categories


@customers.get('/account')
async def get_account_info(user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SAccountInfo:
    user = await BaseCRUD.get_account_info(user_id=user_id)
    return user


@customers.post('/add_or_edit_basket', status_code=201)
async def add_basket_by_product_id(param: Annotated[SBasket, Depends()],
                                   user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SOkResponse:
    await BaseCRUD.add_basket(param=param, user_id=user_id)
    return SOkResponse()


@customers.delete('/delete_basket')
async def delete_basket_by_id(param: Annotated[SOrderId, Depends()],
                              user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SOkResponse:

    order_id = await BaseCRUD.delete_basket(param=param, user_id=user_id)
    return SOkResponse()
