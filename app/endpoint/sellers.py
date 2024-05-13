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
from app.schemas.seller import SCompany, SSellerCom, SCompanyUpdate, SSellerId, SProducts, SParameters
from app.schemas.user import SUserSignUp, SToken, STokenResponse, SOkResponse
from app.core.config import settings

sellers = APIRouter(
    prefix="/api/v1/sellers",
    tags=['sellers'],
    dependencies=[Depends(access_seller)]
)


@sellers.post('/add_company')
async def create_company(seller: Annotated[SSellerCom, Depends()],
                         company: Annotated[SCompany, Depends()], request: Request) -> SOkResponse:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    await BaseCRUD.create_company(seller=seller, company=company, user_id=user_id)
    return SOkResponse()


@sellers.patch('/edit_company')
async def edit_company(param: Annotated[SCompanyUpdate, Depends()],
                       request: Request,
                       file: UploadFile | None = None):
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    if file is not None:
        user_id = await BaseCRUD.update_company(param=param, user_id=user_id, is_add_photo=True)
        create_img(user_id=user_id, files=file, source='company')

    else:
        await BaseCRUD.update_company(param=param, user_id=user_id)
    return SOkResponse()


@sellers.post('add_product')
async def add_product(param: Annotated[SProducts, Depends()], request: Request,
                      categories: str,
                      # details: Annotated[SParameters, Depends()],
                      file: list[UploadFile] = File(...)) -> SOkResponse:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    product_id = await BaseCRUD.add_product_seller(user_id=user_id, param=param,
                                                   categories=categories,
                                                   # details=details,
                                                   photos=file)
    if file is not None:

        create_img(user_id=product_id, source='product', files=file)
    return SOkResponse()
