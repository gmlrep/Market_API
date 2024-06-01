import shutil
from pprint import pprint
from typing import Annotated

from PIL import Image
from fastapi import APIRouter, Depends, HTTPException, Response, File, UploadFile
from fastapi.requests import Request
from fastapi_cache.decorator import cache

from app.core.redis_client import Redis
from app.core.security import create_img, pagination_param
from app.core.dependencies import access_customer, get_user_id_by_token
from app.db.CRUD import BaseCRUD
from app.schemas.customer import SCategory, SProductsInfo, SProduct, SAccountInfo, SCategories, SBasket, SOrderId, \
    SReviewAdd, SContact, SPagination, SReviewInfo
from app.schemas.user import SOkResponse, SUserEdit
from app.services.customers import CustomersService

customers = APIRouter(
    prefix="/api/v1/customers",
    tags=['Customers'],
    dependencies=[Depends(access_customer)]
)


@customers.put('/profile')
async def edit_profile(param: Annotated[SUserEdit, Depends()],
                       user_id: Annotated[int, Depends(get_user_id_by_token)],
                       file: UploadFile = None) -> SOkResponse:
    await CustomersService().update_profile(data=param, user_id=user_id, file=file)
    create_img(user_id=user_id, files=file, source='users') if file is not None else ...
    return SOkResponse()


@customers.get('/category/{category}')
@cache(expire=60)
async def get_product_by_category(param: Annotated[SCategory, Depends()],
                                  pagination: SPagination = Depends(pagination_param)) -> list[SProductsInfo]:
    products = await BaseCRUD.get_products_category(category_name=param.category)
    return products[pagination.start:pagination.end]


@customers.get('/product/{product_id}')
async def get_product_by_id(param: Annotated[SProduct, Depends()]) -> SProductsInfo:
    product = await BaseCRUD.get_product_by_product_id(product_id=param.product_id)
    return product


@customers.get('/category')
@cache(expire=60)
async def get_category_list() -> list[SCategories]:
    categories = await CustomersService().get_categories()
    return categories


@customers.get('/account')
async def get_account_info(user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SAccountInfo:
    user = await BaseCRUD.get_account_info(user_id=user_id)
    return user


@customers.post('/basket', status_code=201)
async def add__or_edit_basket_by_product_id(param: Annotated[SBasket, Depends()],
                                            user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SOkResponse:
    await CustomersService().add_basket(data=param, user_id=user_id)
    return SOkResponse()


@customers.delete('/basket')
async def delete_basket_by_id(param: Annotated[SOrderId, Depends()],
                              user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SOkResponse:
    order_id = await CustomersService().delete_basket(data=param, user_id=user_id)
    return SOkResponse()


@customers.post('/review')
async def add_review_of_product(param: Annotated[SReviewAdd, Depends()],
                                user_id: Annotated[int, Depends(get_user_id_by_token)],
                                photos: list[UploadFile] = None) -> SOkResponse:
    review_id = await CustomersService().add_review(data=param, user_id=user_id, photos=photos)
    create_img(user_id=review_id, source='review', files=photos) if photos is not None else ...
    return SOkResponse()


@customers.post('/contact')
async def add_contact_info(param: Annotated[SContact, Depends()],
                           user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SOkResponse:
    await CustomersService().add_contacts(data=param, user_id=user_id)
    return SOkResponse()


@customers.put('/contact')
async def edit_contact_info(param: Annotated[SContact, Depends()],
                            user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SOkResponse:
    await CustomersService().edit_contacts(data=param, user_id=user_id)
    return SOkResponse()


@customers.get('/review')
async def get_review_by_product_id(param: Annotated[SProduct, Depends()],
                                   pagination: SPagination = Depends(pagination_param)) -> list[SReviewInfo]:
    reviews = await BaseCRUD.get_review_by_product_id(param=param)
    return reviews[pagination.start:pagination.end]
