from fastapi import UploadFile

from app.core.exceptions import AuthError, NotFoundError
from app.core.security import get_manager_to_add
from app.repository.seller import SellerRepository, CompanyRepository, ProductRepository
from app.repository.user import UserRepository
from app.schemas.seller import (
    SSellerCom,
    SCompanyAdd,
    SCompanyUpdate,
    SSellerAdd,
    SManagerSignUp,
    SProducts,
    SProductDelete,
)
from app.services.base import BaseService


class SellersService(BaseService):
    def __init__(
        self,
        seller_repository: SellerRepository,
        company_repository: CompanyRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
    ):
        super().__init__(repository=seller_repository)
        self.seller_repository = seller_repository
        self.company_repository = company_repository
        self.product_repository = product_repository
        self.user_repository = user_repository

    async def add_company(
        self, company: SCompanyAdd, seller: SSellerCom, user_id: int
    ) -> int:
        seller_id = await self.seller_repository.find_id(filter_by={"user_id": user_id})
        if seller_id:
            raise AuthError(detail="Seller and company already exist")
        company_row = await self.company_repository.create(company.model_dump())
        company_id = company_row.id
        rep = SSellerAdd(
            type_company=seller.type_company,
            company_id=company_id,
            user_id=user_id,
            company_role=1,
        )
        await self.seller_repository.create(rep.model_dump())
        return company_id

    async def update_company(
        self, data: SCompanyUpdate, user_id: int, file: UploadFile | None = None
    ) -> int:
        company_param = data.model_dump(exclude_none=True)
        if file is not None:
            company_param["photo"] = f"company{user_id}_1.jpg"
        company_id = await self.company_repository.update_by_seller_user(
            user_id=user_id, values=company_param
        )
        return company_id

    async def add_manager(self, user_id: int, param: SManagerSignUp) -> int:
        from app.services.users import UsersService

        manager = await get_manager_to_add(param=param)
        users_service = UsersService(user_repository=self.user_repository)
        manager_id = await users_service.add_one(data=manager)
        company_info = await self.seller_repository.get_seller_by_user(user_id=user_id)
        if not company_info:
            raise NotFoundError(detail="Company not found")
        seller = await self.seller_repository.create(
            {
                "company_role": 2,
                "user_id": manager_id,
                "type_company": company_info.type_company,
                "company_id": company_info.company_id,
            }
        )
        return seller.id

    async def add_product(self, param: SProducts, user_id: int, categories: str, photos) -> int:
        return await self.product_repository.add_product_with_photos(
            param=param, user_id=user_id, categories=categories, photos=photos
        )

    async def add_parameters(self, param: dict, user_id: int, product_id: int) -> None:
        await self.product_repository.add_parameters(
            param=param, user_id=user_id, product_id=product_id
        )

    async def delete_product(self, param: SProductDelete, user_id: int) -> int:
        return await self.product_repository.delete_for_seller(param=param, user_id=user_id)
