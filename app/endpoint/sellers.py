from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.core.security import create_img
from app.core.dependencies import access_seller, get_user_id_by_token
from app.db.CRUD import BaseCRUD
from app.processes.processes import send_verify_email
from app.schemas.seller import SCompanyAdd, SSellerCom, SCompanyUpdate, SProducts, SProductDelete, \
    SManagerSignUp
from app.schemas.user import SOkResponse
from app.services.sellers import SellersService

sellers = APIRouter(
    prefix="/api/v1/sellers",
    tags=['Sellers'],
    dependencies=[Depends(access_seller)]
)


@sellers.post('/company', status_code=201)
async def create_company(seller: Annotated[SSellerCom, Depends()],
                         company: Annotated[SCompanyAdd, Depends()],
                         user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SOkResponse:
    await SellersService().add_company(company=company, seller=seller, user_id=user_id)
    return SOkResponse()


@sellers.put('/company')
async def edit_company(param: Annotated[SCompanyUpdate, Depends()],
                       user_id: Annotated[int, Depends(get_user_id_by_token)],
                       file: UploadFile | None = None) -> SOkResponse:
    company_id = await SellersService().update_company(data=param, user_id=user_id, file=file)
    create_img(user_id=company_id, files=file, source='company') if file is not None else ...
    return SOkResponse()


@sellers.post('/product', status_code=201)
async def add_product(param: Annotated[SProducts, Depends()],
                      user_id: Annotated[int, Depends(get_user_id_by_token)],
                      categories: str,
                      file: list[UploadFile] = None) -> SOkResponse:
    product_id = await BaseCRUD.add_product_seller(user_id=user_id, param=param,
                                                   categories=categories,
                                                   photos=file)
    create_img(user_id=product_id, source='product', files=file) if file is not None else ...

    return SOkResponse()


@sellers.post('/parameters', status_code=201)
async def add_parameters(param: dict,
                         user_id: Annotated[int, Depends(get_user_id_by_token)],
                         product_id: int) -> SOkResponse:
    await BaseCRUD.add_parameters(param=param, user_id=user_id, product_id=product_id)
    return SOkResponse()


@sellers.delete('/product')
async def delete_product_by_id(param: Annotated[SProductDelete, Depends()],
                               user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SOkResponse:
    await BaseCRUD.delete_product(param=param, user_id=user_id)
    return SOkResponse()


@sellers.post('/manager', status_code=201)
async def add_manager(param: Annotated[SManagerSignUp, Depends()],
                      user_id: Annotated[int, Depends(get_user_id_by_token)]) -> SOkResponse:
    await SellersService().add_manager(user_id=user_id, param=param)
    send_verify_email.delay(user_id=user_id, email=param.email)
    return SOkResponse()
