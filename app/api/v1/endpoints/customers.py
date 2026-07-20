from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, UploadFile
from fastapi_cache.decorator import cache

from app.core.container import Container
from app.core.dependencies import access_customer, get_user_id_by_token
from app.core.middleware.inject import inject
from app.core.security import create_img, pagination_param
from app.schemas.customer import (
    SProductsInfo,
    SProduct,
    SAccountInfo,
    SCategories,
    SBasket,
    SOrderId,
    SReviewAdd,
    SContact,
    SPagination,
    SReviewInfo,
)
from app.schemas.user import SOkResponse, SUserEdit
from app.services.customers import CustomersService

customers = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(access_customer)],
)


@customers.put("/profile")
@inject
async def edit_profile(
    param: Annotated[SUserEdit, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    file: UploadFile = None,
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> SOkResponse:
    await service.update_profile(data=param, user_id=user_id, file=file)
    if file is not None:
        create_img(user_id=user_id, files=[file], source="users")
    return SOkResponse()


@customers.get("/category/{category}")
@cache(expire=60)
@inject
async def get_product_by_category(
    category: str,
    pagination: SPagination = Depends(pagination_param),
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> list[SProductsInfo]:
    products = await service.get_products_by_category(category_name=category)
    return products[pagination.start : pagination.end]


@customers.get("/product/{product_id}")
@inject
async def get_product_by_id(
    param: Annotated[SProduct, Depends()],
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> SProductsInfo:
    return await service.get_product(product_id=param.product_id)


@customers.get("/category")
@cache(expire=60)
@inject
async def get_category_list(
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> list[SCategories]:
    return await service.get_categories()


@customers.get("/account")
@inject
async def get_account_info(
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> SAccountInfo:
    return await service.get_account(user_id=user_id)


@customers.post("/basket", status_code=201)
@inject
async def add_or_edit_basket_by_product_id(
    param: Annotated[SBasket, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> SOkResponse:
    await service.add_basket(data=param, user_id=user_id)
    return SOkResponse()


@customers.delete("/basket")
@inject
async def delete_basket_by_id(
    param: Annotated[SOrderId, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> SOkResponse:
    await service.delete_basket(data=param, user_id=user_id)
    return SOkResponse()


@customers.post("/review")
@inject
async def add_review_of_product(
    param: Annotated[SReviewAdd, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    photos: list[UploadFile] = None,
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> SOkResponse:
    review_id = await service.add_review(data=param, user_id=user_id, photos=photos)
    if photos is not None:
        create_img(user_id=review_id, source="review", files=photos)
    return SOkResponse()


@customers.post("/contact", status_code=201)
@inject
async def add_contact_info(
    param: Annotated[SContact, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> SOkResponse:
    await service.add_contacts(data=param, user_id=user_id)
    return SOkResponse()


@customers.put("/contact")
@inject
async def edit_contact_info(
    param: Annotated[SContact, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> SOkResponse:
    await service.edit_contacts(data=param, user_id=user_id)
    return SOkResponse()


@customers.get("/review")
@inject
async def get_review_by_product_id(
    param: Annotated[SProduct, Depends()],
    pagination: SPagination = Depends(pagination_param),
    service: Annotated[
        CustomersService, Depends(Provide[Container.customer_service])
    ] = None,
) -> list[SReviewInfo]:
    reviews = await service.get_reviews(param=param)
    return reviews[pagination.start : pagination.end]
