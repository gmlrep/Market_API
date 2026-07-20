from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, UploadFile

from app.core.container import Container
from app.core.dependencies import access_seller, get_user_id_by_token
from app.core.middleware.inject import inject
from app.core.security import create_img
from app.processes.processes import send_verify_email
from app.schemas.seller import (
    SCompanyAdd,
    SSellerCom,
    SCompanyUpdate,
    SProducts,
    SProductDelete,
    SManagerSignUp,
)
from app.schemas.user import SOkResponse
from app.services.sellers import SellersService

sellers = APIRouter(
    prefix="/sellers",
    tags=["Sellers"],
    dependencies=[Depends(access_seller)],
)


@sellers.post("/company", status_code=201)
@inject
async def create_company(
    seller: Annotated[SSellerCom, Depends()],
    company: Annotated[SCompanyAdd, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    service: Annotated[SellersService, Depends(Provide[Container.seller_service])] = None,
) -> SOkResponse:
    await service.add_company(company=company, seller=seller, user_id=user_id)
    return SOkResponse()


@sellers.put("/company")
@inject
async def edit_company(
    param: Annotated[SCompanyUpdate, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    file: UploadFile | None = None,
    service: Annotated[SellersService, Depends(Provide[Container.seller_service])] = None,
) -> SOkResponse:
    company_id = await service.update_company(data=param, user_id=user_id, file=file)
    if file is not None:
        create_img(user_id=company_id, files=[file], source="company")
    return SOkResponse()


@sellers.post("/product", status_code=201)
@inject
async def add_product(
    param: Annotated[SProducts, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    categories: str,
    file: list[UploadFile] = None,
    service: Annotated[SellersService, Depends(Provide[Container.seller_service])] = None,
) -> SOkResponse:
    product_id = await service.add_product(
        user_id=user_id, param=param, categories=categories, photos=file
    )
    if file is not None:
        create_img(user_id=product_id, source="product", files=file)
    return SOkResponse()


@sellers.post("/parameters", status_code=201)
@inject
async def add_parameters(
    param: dict,
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    product_id: int,
    service: Annotated[SellersService, Depends(Provide[Container.seller_service])] = None,
) -> SOkResponse:
    await service.add_parameters(param=param, user_id=user_id, product_id=product_id)
    return SOkResponse()


@sellers.delete("/product")
@inject
async def delete_product_by_id(
    param: Annotated[SProductDelete, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    service: Annotated[SellersService, Depends(Provide[Container.seller_service])] = None,
) -> SOkResponse:
    await service.delete_product(param=param, user_id=user_id)
    return SOkResponse()


@sellers.post("/manager", status_code=201)
@inject
async def add_manager(
    param: Annotated[SManagerSignUp, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    service: Annotated[SellersService, Depends(Provide[Container.seller_service])] = None,
) -> SOkResponse:
    await service.add_manager(user_id=user_id, param=param)
    send_verify_email.delay(user_id=user_id, email=param.email)
    return SOkResponse()
