from fastapi import HTTPException, UploadFile
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

from app.db.database import Base
from app.db.models import Users, Sellers, Products, Category, Parameters, Photos, Reviews
from app.schemas.customer import SProductsInfo, SAccountInfo, SProduct, SReviewInfo
from app.schemas.seller import SProducts, SProductDelete
from app.db.database import async_engine, async_session


class BaseCRUD:
    # Sellers
    @classmethod
    async def add_product_seller(cls, param: SProducts, user_id: int, categories: str,
                                 photos: list[UploadFile]) -> int:
        async with async_session() as session:
            company_id = (await session.execute(select(Sellers.company_id).filter_by(user_id=user_id))).scalar()
            categories_id = (await session.execute(select(Category.id).filter_by(name=categories))).scalar()
            product_param = param.model_dump(exclude_none=True)
            product_param.update(company_id=company_id, category_id=categories_id)
            product = Products(**product_param)
            session.add(product)
            await session.flush()
            await session.commit()
            product_id = product.id

            if photos is not None:
                for i, photo in enumerate(photos):
                    file = Photos(product_id=product_id, photo=f'product{product_id}_{i + 1}.jpg')
                    session.add(file)
                    await session.commit()
            return product_id

    @classmethod
    async def add_parameters(cls, param: dict, user_id: int, product_id: int):
        async with async_session() as session:
            product = (await session.execute(select(Products.id).where(
                Products.id == product_id, Products.company_id == (select(
                    Sellers.company_id).filter_by(user_id=user_id)).scalar_subquery()))).scalar()
            if product is None:
                raise HTTPException(
                    status_code=404,
                    detail='Product not found'
                )
            if param is not None:
                param = [{'name': key, 'description': value, 'product_id': product_id} for key, value in param.items()]
                for detail in param:
                    parameters = Parameters(**detail)
                    session.add(parameters)
                    await session.commit()

    @classmethod
    async def delete_product(cls, param: SProductDelete, user_id: int):
        async with async_session() as session:
            company_id = (await session.execute(select(Sellers.company_id).filter_by(user_id=user_id))).scalar()
            product_id = (await session.execute(delete(Products).filter_by(
                id=param.product_id, company_id=company_id).returning(Products.id))).scalar()
            await session.commit()
            if product_id is None:
                raise HTTPException(
                    status_code=404,
                    detail='Product not found'
                )

    @classmethod
    async def add_manager(cls, user_id: int, manager_id: int):
        async with async_session() as session:
            company_info = (await session.execute(select(Sellers.company_id, Sellers.type_company).filter_by(user_id=user_id))).first()
            if company_info is None:
                raise HTTPException(
                    status_code=404,
                    detail='Company not found'
                )
            manager = Sellers(company_role=2, user_id=manager_id,
                              type_company=company_info[1], company_id=company_info[0])
            session.add(manager)
            await session.commit()

    # Customers
    @classmethod
    async def get_products_category(cls, category_name: str) -> list[SProductsInfo]:
        async with async_session() as session:
            products = (await session.execute(select(Products).where(
                Products.category_id == (select(Category.id).filter_by(
                    name=category_name)).scalar_subquery()).options(
                selectinload(Products.photo), selectinload(Products.parameter)))).scalars().all()

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
            products = (await session.execute(select(Products).filter_by(
                id=product_id).options(selectinload(Products.photo), selectinload(Products.parameter)))).first()
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
            user_resp = (await session.execute(select(Users).filter_by(id=user_id).options(
                selectinload(Users.order), selectinload(Users.contact)))).first()
            if user_resp is None:
                raise HTTPException(
                    status_code=404,
                    detail='User not found'
                )
            user = [SAccountInfo.model_validate(result, from_attributes=True) for result in user_resp]
            return user[0]

    @classmethod
    async def get_review_by_product_id(cls, param: SProduct) -> list[SReviewInfo]:
        async with async_session() as session:
            resp = (await session.execute(select(Reviews).filter_by(product_id=param.product_id).options(
                selectinload(Reviews.photo), selectinload(Reviews.user)))).scalars().all()
            reviews = [SReviewInfo.model_validate(result, from_attributes=True) for result in resp]
            return reviews
