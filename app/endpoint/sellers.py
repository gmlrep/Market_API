import json
import shutil
from pprint import pprint
from typing import Annotated, Dict

from PIL import Image
from redis import asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Response, Request, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from app.core.redis_client import Redis
from app.core.security import get_hashed_psw, authenticate_user, create_access_token, create_refresh_token, decode_jwt, \
    create_img, is_refresh_token, access_seller
from app.db.CRUD import BaseCRUD
from app.schemas.seller import SCompany, SSellerCom, SCompanyUpdate, SSellerId, SProducts, SParameters, SProductDelete
from app.schemas.user import SUserSignUp, SToken, STokenResponse, SOkResponse
from app.core.config import settings

sellers = APIRouter(
    prefix="/api/v1/sellers",
    tags=['sellers'],
    dependencies=[Depends(access_seller)]
)


@sellers.post('/add_company', status_code=201)
async def create_company(seller: Annotated[SSellerCom, Depends()],
                         company: Annotated[SCompany, Depends()], request: Request) -> SOkResponse:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    await BaseCRUD.create_company(seller=seller, company=company, user_id=user_id)
    return SOkResponse()


@sellers.put('/edit_company')
async def edit_company(param: Annotated[SCompanyUpdate, Depends()],
                       request: Request,
                       file: UploadFile | None = None):
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    company_id = await BaseCRUD.update_company(param=param, user_id=user_id, file=file)
    create_img(user_id=company_id, files=file, source='company') if file is not None else ...
    return SOkResponse()


@sellers.post('add_product', status_code=201)
async def add_product(param: Annotated[SProducts, Depends()], request: Request,
                      categories: str,
                      file: list[UploadFile] = None) -> SOkResponse:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    product_id = await BaseCRUD.add_product_seller(user_id=user_id, param=param,
                                                   categories=categories,
                                                   photos=file)
    create_img(user_id=product_id, source='product', files=file) if file is not None else ...

    return SOkResponse()


@sellers.post('/add_parameters', status_code=201)
async def add_parameters(param: dict, request: Request, product_id: int) -> SOkResponse:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    await BaseCRUD.add_parameters(param=param, user_id=user_id, product_id=product_id)
    return SOkResponse()


@sellers.delete('product')
async def delete_product_by_id(param: Annotated[SProductDelete, Depends()], request: Request) -> SOkResponse:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    await BaseCRUD.delete_product(param=param, user_id=user_id)
    return SOkResponse()
