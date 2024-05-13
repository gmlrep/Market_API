import asyncio

from fastapi import HTTPException, UploadFile
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError

from app.db.database import Base
from app.db.models import Users, Sellers, Companies, Products, Category, Parameters, Photos
from app.schemas.admin import SCategoryAdd, SUserId
from app.schemas.customer import SCategory, SProductsInfo, SAccountInfo
from app.schemas.seller import SCompany, SSellerCom, SCompanyUpdate, SSellerId, SProducts, SParameters
from app.schemas.task import STask, SUserTask
from app.schemas.user import SUserAdd, SUserInfo, SUserEdit
from app.db.database import async_engine, async_session


class BaseCRUD:

    @classmethod
    async def create_table(cls):
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def delete_table(cls):
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    # Auth
    @classmethod
    async def add_user(cls, data: SUserAdd) -> int:
        async with async_session() as session:
            user_param = data.model_dump()
            user = Users(**user_param)
            try:
                session.add(user)
                await session.flush()
                await session.commit()
                return user.id

            except IntegrityError:
                raise HTTPException(
                    status_code=401,
                    detail='User with this username or email are exists'
                )

    @classmethod
    async def get_user(cls, email: str) -> SUserInfo | bool:
        async with async_session() as session:
            response = await session.execute(select(Users).filter_by(email=email))
            resp = response.first()
            if not resp:
                return False
            user = [SUserInfo.model_validate(result, from_attributes=True) for result in resp]
            return user[0]

    # Sellers
    @classmethod
    async def create_company(cls, company: SCompany, seller: SSellerCom, user_id: int):
        async with async_session() as session:
            company_param = company.model_dump()
            company = Companies(**company_param)
            session.add(company)
            await session.flush()
            await session.commit()
            company_id = company.id
            seller_param = seller.model_dump()
            seller_param.update(company_id=company_id, user_id=user_id, company_role=1)
            seller = Sellers(**seller_param)
            session.add(seller)
            await session.commit()

    @classmethod
    async def update_company(cls, param: SCompanyUpdate, user_id: SSellerId, is_add_photo: bool = False) -> int:
        async with async_session() as session:
            company_param = {key: value for key, value in param.model_dump().items() if value is not None}
            company_param.update(photo=True) if is_add_photo else ...
            company_id = await session.execute(update(Companies).where(
                Companies.id == (select(Sellers.company_id).filter_by(
                    user_id=user_id.user_id)).scalar_subquery()).values(**company_param).returning(Companies.id))
            await session.commit()
            return company_id.scalar()

    @classmethod
    async def add_product_seller(cls, param: SProducts, user_id: int, categories: str,
                                 # details: SParameters,
                                 photos: list[UploadFile]) -> int:
        async with async_session() as session:
            company_id = (await session.execute(select(Sellers.company_id).filter_by(user_id=user_id))).scalar()
            categories_id = (await session.execute(select(Category.id).filter_by(name=categories))).scalar()
            prodict_param = param.model_dump()
            prodict_param.update(company_id=company_id, category_id=categories_id)
            product = Products(**prodict_param)
            session.add(product)
            await session.flush()
            await session.commit()
            product_id = product.id

            if photos is not None:
                for photo in photos:
                    file = Photos(product_id=product_id)
                    session.add(file)
                    await session.commit()
            # details_param = details.model_dump()
            # if details_param is not None:
            #     param = {{'name': key, 'description': value} for key, value in details_param.items()}
            #     for detail in param:
            #         parameters = Parameters(**detail)
            #         session.add(parameters)
            #         await session.commit()
            return product_id

    # Customers
    @classmethod
    async def edit_profile_user(cls, param: SUserEdit, user_id: int):
        async with async_session() as session:
            user_param = {key: value for key, value in param.model_dump().items() if value is not None}
            if user_param == {}:
                return
            await session.execute(update(Users).filter_by(id=user_id).values(**user_param))
            await session.commit()

    @classmethod
    async def get_products_category(cls, category_id: int) -> list[SProductsInfo]:
        async with async_session() as session:
            # products = (await session.execute(select(Products).filter_by(category_id=category_id))).scalars().all()

            products = await session.execute(
                select(Products).filter_by(category_id=category_id).join(Photos, Products.id == Photos.product_id))
            products = products.scalars().all()
            if products is None:
                raise HTTPException(
                    status_code=404,
                    detail='Products not found in this category'
                )
            products_model = [SProductsInfo.model_validate(result, from_attributes=True) for result in products]
        return products_model

    @classmethod
    async def get_product_by_product_id(cls, product_id: int) -> SProductsInfo:
        async with async_session() as session:
            products = (await session.execute(select(Products).filter_by(id=product_id))).first()
            if products is None:
                raise HTTPException(
                    status_code=404,
                    detail='Product not found'
                )
            product_model = [SProductsInfo.model_validate(result, from_attributes=True) for result in products]
            return product_model[0]

    @classmethod
    async def get_account_info(cls, user_id: int) -> SAccountInfo:
        async with async_session() as session:
            user_resp = (await session.execute(select(Users).filter_by(id=user_id))).first()
            if user_resp is None:
                raise HTTPException(
                    status_code=404,
                    detail='User not found'
                )
            user = [SAccountInfo.model_validate(result, from_attributes=True) for result in user_resp]
            return user[0]

    # Admins
    @classmethod
    async def add_category(cls, param: SCategoryAdd):
        async with async_session() as session:
            category_param = param.model_dump()
            category = Category(**category_param)
            session.add(category)
            await session.commit()

    @classmethod
    async def ban_user(cls, param: SUserId):
        async with async_session() as session:
            await session.execute(update(Users).filter_by(id=param.user_id).values(is_enable=False))
            await session.commit()