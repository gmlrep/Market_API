from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models import Sellers, Companies, Products, Category, Parameters, Photos
from app.repository.base import BaseRepository, SessionFactory
from app.schemas.customer import SProductsInfo
from app.schemas.seller import SProducts, SProductDelete, SSellerAdd


class SellerRepository(BaseRepository):
    def __init__(self, session: SessionFactory):
        super().__init__(session=session, model=Sellers)

    async def get_company_id_by_user(self, user_id: int) -> int | None:
        async with self.session() as session:
            result = await session.execute(
                select(Sellers.company_id).filter_by(user_id=user_id)
            )
            return result.scalar_one_or_none()

    async def get_seller_by_user(self, user_id: int) -> SSellerAdd | None:
        return await self.find_one(filter_by={"user_id": user_id}, schema=SSellerAdd)


class CompanyRepository(BaseRepository):
    def __init__(self, session: SessionFactory):
        super().__init__(session=session, model=Companies)

    async def update_by_seller_user(self, user_id: int, values: dict) -> int | None:
        async with self.session() as session:
            stmt = (
                update(Companies)
                .where(
                    Companies.id
                    == (
                        select(Sellers.company_id).filter_by(user_id=user_id)
                    ).scalar_subquery()
                )
                .values(**values)
                .returning(Companies.id)
            )
            resp = await session.execute(stmt)
            await session.commit()
            return resp.scalar_one_or_none()


class ProductRepository(BaseRepository):
    def __init__(self, session: SessionFactory):
        super().__init__(session=session, model=Products)

    async def add_product_with_photos(
        self, param: SProducts, user_id: int, categories: str, photos
    ) -> int:
        async with self.session() as session:
            company_id = (
                await session.execute(select(Sellers.company_id).filter_by(user_id=user_id))
            ).scalar()
            categories_id = (
                await session.execute(select(Category.id).filter_by(name=categories))
            ).scalar()
            product_param = param.model_dump(exclude_none=True)
            product_param.update(company_id=company_id, category_id=categories_id)
            product = Products(**product_param)
            session.add(product)
            await session.flush()
            product_id = product.id
            if photos is not None:
                for i, _photo in enumerate(photos):
                    session.add(
                        Photos(product_id=product_id, photo=f"product{product_id}_{i + 1}.jpg")
                    )
            await session.commit()
            return product_id

    async def add_parameters(self, param: dict, user_id: int, product_id: int) -> None:
        async with self.session() as session:
            product = (
                await session.execute(
                    select(Products.id).where(
                        Products.id == product_id,
                        Products.company_id
                        == (
                            select(Sellers.company_id).filter_by(user_id=user_id)
                        ).scalar_subquery(),
                    )
                )
            ).scalar()
            if product is None:
                raise NotFoundError(detail="Product not found")
            if param is not None:
                for key, value in param.items():
                    session.add(
                        Parameters(name=key, description=value, product_id=product_id)
                    )
                await session.commit()

    async def delete_for_seller(self, param: SProductDelete, user_id: int) -> int:
        from sqlalchemy import delete

        async with self.session() as session:
            company_id = (
                await session.execute(select(Sellers.company_id).filter_by(user_id=user_id))
            ).scalar()
            product_id = (
                await session.execute(
                    delete(Products)
                    .filter_by(id=param.product_id, company_id=company_id)
                    .returning(Products.id)
                )
            ).scalar()
            await session.commit()
            if product_id is None:
                raise NotFoundError(detail="Product not found")
            return product_id

    async def get_by_category_name(self, category_name: str) -> list[SProductsInfo]:
        async with self.session() as session:
            products = (
                (
                    await session.execute(
                        select(Products)
                        .where(
                            Products.category_id
                            == (
                                select(Category.id).filter_by(name=category_name)
                            ).scalar_subquery()
                        )
                        .options(
                            selectinload(Products.photo),
                            selectinload(Products.parameter),
                        )
                    )
                )
                .scalars()
                .all()
            )
            return [
                SProductsInfo.model_validate(result, from_attributes=True)
                for result in products
            ]

    async def get_product_info(self, product_id: int) -> SProductsInfo:
        async with self.session() as session:
            row = (
                await session.execute(
                    select(Products)
                    .filter_by(id=product_id)
                    .options(
                        selectinload(Products.photo),
                        selectinload(Products.parameter),
                    )
                )
            ).scalars().first()
            if row is None:
                raise NotFoundError(detail="Product not found")
            return SProductsInfo.model_validate(row, from_attributes=True)
