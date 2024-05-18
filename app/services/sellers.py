from fastapi import HTTPException, UploadFile

from app.core.security import get_manager_to_add
from app.db.models import Users, Sellers, Companies, Products
from app.repositories.crud import SQLAlchemyRepository
from app.schemas.seller import SSellerCom, SCompanyAdd, SCompanyUpdate, SSellerAdd, SManagerSignUp
from app.services.users import UsersService


class SellersService:
    def __init__(self):
        self.seller_repo = SQLAlchemyRepository(model=Sellers)
        self.company_repo = SQLAlchemyRepository(model=Companies)
        self.product_repo = SQLAlchemyRepository(model=Products)

    async def add_company(self, company: SCompanyAdd, seller: SSellerCom, user_id: int) -> int:
        seller_id = await self.seller_repo.find_id(filter_by={'id': user_id})
        print(seller_id)
        if seller_id:
            raise HTTPException(
                status_code=403,
                detail='Seller and company already exist'
            )
        company_id = await self.company_repo.create(data=company.model_dump())
        rep = SSellerAdd(type_company=seller.type_company, company_id=company_id, user_id=user_id, company_role=1)
        seller_id = await self.seller_repo.create(data=rep.model_dump())
        return company_id

    async def update_company(self, data: SCompanyUpdate, user_id: int, file: UploadFile | None = None) -> int:
        company_param = data.model_dump(exclude_none=True)
        company_param.update(photo=f'company{user_id}_1.jpg') if file is not None else ...

        company_id = await self.company_repo.update_company(filter_by={'user_id': user_id},
                                                            sub_model=Sellers, values=company_param)
        return company_id

    async def add_manager(self, user_id: int, param: SManagerSignUp) -> int:
        manager = await get_manager_to_add(param=param)
        manager_id = await UsersService().add_one(data=manager)
        company_info = await self.seller_repo.read(filter_by={'user_id': user_id}, schema=SSellerAdd)
        if not company_info:
            raise HTTPException(
                status_code=404,
                detail='Company not found'
            )
        seller_id = await self.seller_repo.create(data={'company_role': 2, 'user_id': manager_id,
                                                        'type_company': company_info.type_company,
                                                        'company_id': company_info.company_id})
        return seller_id

    # async def add_product(self, data: SProducts, user_id: int, categories: str, photos: list[UploadFile]) -> int:
    #     resp = await self.seller_repo.find_id()
    #     await self.product_repo.create(data=)
