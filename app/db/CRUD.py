from fastapi import HTTPException, UploadFile
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.database import Base
from app.db.models import Users, Sellers, Companies, Products, Category, Parameters, Photos, Contacts, Orders, Reviews, \
    PhotoReview
from app.schemas.customer import SCategory, SProductsInfo, SAccountInfo, SCategories, SBasket, SOrderId, SReviewAdd, \
    SContact, SProduct, SReviewInfo
from app.schemas.seller import SCompanyAdd, SSellerCom, SCompanyUpdate, SProducts, SProductDelete, \
    SManagerAdd
from app.schemas.user import SUserAdd, SUserInfo, SUserEdit, HashedPasswordSalt
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
    async def add_user(cls, data: SUserAdd | SManagerAdd) -> int:
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

    @classmethod
    async def get_user_by_token_id(cls, user_id: int) -> SUserInfo:
        async with async_session() as session:
            resp = (await session.execute(select(Users).filter_by(id=user_id))).first()
            user = [SUserInfo.model_validate(result, from_attributes=True) for result in resp]
            return user[0]

    @classmethod
    async def update_password(cls, param: HashedPasswordSalt, user_id: int):
        async with async_session() as session:
            await session.execute(update(Users).filter_by(id=user_id).values(
                hashed_password=param.hashed_password, salt=param.salt))
            await session.commit()

    @classmethod
    async def verify_email(cls, user_id: int):
        async with async_session() as session:
            user_id = (await session.execute(update(Users).filter_by(
                id=user_id).values(is_enabled=True).returning(Users.id))).scalar()
            print(user_id)
            if not user_id:
                raise HTTPException(
                    status_code=403,
                    detail='User does not exist'
                )
            await session.commit()

    @classmethod
    async def deactivate_account(cls, user_id: int):
        async with async_session() as session:
            await session.execute(update(Users).filter_by(id=user_id).values(is_active=False))
            await session.commit()

    # Sellers
    @classmethod
    async def create_company(cls, company: SCompanyAdd, seller: SSellerCom, user_id: int):
        async with async_session() as session:
            seller_id = (await session.execute(select(Sellers.id).filter_by(user_id=user_id))).scalar()
            if seller_id is not None:
                raise HTTPException(
                    status_code=403,
                    detail='Seller and company already exist'
                )
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
    async def update_company(cls, param: SCompanyUpdate, user_id: int, file: UploadFile) -> int:
        async with async_session() as session:
            company_param = param.model_dump(exclude_none=True)
            # company_param = {key: value for key, value in param.model_dump().items() if value is not None}
            company_param.update(photo=f'company{user_id}_1.jpg') if file is not None else ...

            company_id = await session.execute(update(Companies).where(
                Companies.id == (select(Sellers.company_id).filter_by(
                    user_id=user_id.user_id)).scalar_subquery()).values(**company_param).returning(Companies.id))

            await session.commit()
            return company_id.scalar()

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
            print(param)
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

    @classmethod
    async def set_password_by_manager(cls, hashed_password: str, user_id: int, salt: str):
        async with async_session() as session:
            await session.execute(update(Users).filter_by(
                id=user_id).values(hashed_password=hashed_password, salt=salt, is_active=True, is_enabled=True))
            await session.commit()

    # Customers
    @classmethod
    async def edit_profile_user(cls, param: SUserEdit, user_id: int, file: UploadFile):
        async with async_session() as session:

            user_param = param.model_dump(exclude_none=True)
            # user_param = {key: value for key, value in param.model_dump().items() if value is not None}
            if file is not None:
                user_param['photo'] = f'user{user_id}_1.jpg'
            if user_param == {}:
                raise HTTPException(
                    status_code=403,
                    detail='Do not update'
                )
            await session.execute(update(Users).filter_by(id=user_id).values(**user_param))
            await session.commit()

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
                selectinload(Users.order), selectinload(Users.contact)
            ))).first()
            if user_resp is None:
                raise HTTPException(
                    status_code=404,
                    detail='User not found'
                )
            user = [SAccountInfo.model_validate(result, from_attributes=True) for result in user_resp]
            return user[0]

    @classmethod
    async def get_categories(cls) -> list[SCategories]:
        async with async_session() as session:
            categories = (await session.execute(select(Category))).scalars().all()
            cat = [SCategories.model_validate(result, from_attributes=True) for result in categories]
            print(cat)
            return cat

    @classmethod
    async def add_basket(cls, param: SBasket, user_id: int):
        async with async_session() as session:
            contact_id = (await session.execute(select(Contacts.id).filter_by(user_id=user_id))).scalar()
            order_param = param.model_dump(exclude_none=True)
            order_param.update(user_id=user_id)
            order_param.update(contact_id=contact_id) if contact_id is not None else ...

            order_id = (await session.execute(select(Orders.id).filter_by(
                user_id=user_id, is_taken=False, is_order=False, product_id=param.product_id))).scalar()
            if order_id is not None:
                await session.execute(update(Orders).filter_by(id=order_id).values(quantity=param.quantity))
                await session.commit()
                return

            order = Orders(**order_param)
            session.add(order)
            await session.commit()

    @classmethod
    async def delete_basket(cls, param: SOrderId, user_id: int) -> int:
        async with async_session() as session:
            order_id = (await session.execute(delete(Orders).filter_by(
                id=param.order_id, user_id=user_id, is_taken=False, is_order=False).returning(Orders.id))).scalar()
            await session.commit()
            if order_id is None:
                raise HTTPException(
                    status_code=404,
                    detail="Order by this id doesn't exist"
                )
            return order_id

    @classmethod
    async def add_review(cls, param: SReviewAdd, user_id: int, photos: list[UploadFile] = None) -> int:
        async with async_session() as session:
            order_id = (await session.execute(select(Orders.id).filter_by(
                user_id=user_id, product_id=param.product_id, is_taken=True, is_order=True))).scalar()
            if order_id is None:
                raise HTTPException(
                    status_code=404,
                    detail='Order not found'
                )
            review_id = (await session.execute(select(Reviews).filter_by(order_id=order_id))).scalar()
            if review_id is not None:
                raise HTTPException(
                    status_code=403,
                    detail='Review is already exist'
                )
            review_param = param.model_dump()
            review_param.update(user_id=user_id, order_id=order_id)
            review = Reviews(**review_param)
            session.add(review)
            await session.flush()
            await session.commit()
            review_ids = review.id
            print(photos)
            if photos is not None:
                for i, photo in enumerate(photos):
                    file = PhotoReview(review_id=review_ids, photo=f'review{review_ids}_{i + 1}.jpg')
                    session.add(file)
                    await session.commit()
            return review_ids

    @classmethod
    async def add_contacts(cls, param: SContact, user_id: int):
        async with async_session() as session:
            contact_id = (await session.execute(select(Contacts.id).filter_by(user_id=user_id))).scalar()
            if contact_id is not None:
                raise HTTPException(
                    status_code=403,
                    detail='Contacts is already exist'
                )
            contact_param = param.model_dump()
            contact_param.update(user_id=user_id)
            contact = Contacts(**contact_param)
            session.add(contact)
            await session.commit()

    @classmethod
    async def edit_contacts(cls, param: SContact, user_id: int):
        async with async_session() as session:
            contact_id = (await session.execute(select(Contacts.id).filter_by(user_id=user_id))).scalar()
            if contact_id is None:
                raise HTTPException(
                    status_code=404,
                    detail='Contacts does not exist'
                )
            contact_param = param.model_dump()
            await session.execute(update(Contacts).filter_by(user_id=user_id).values(**contact_param))
            await session.commit()

    @classmethod
    async def get_review_by_product_id(cls, param: SProduct) -> list[SReviewInfo]:
        async with async_session() as session:
            resp = (await session.execute(select(Reviews).filter_by(product_id=param.product_id).options(
                selectinload(Reviews.photo), selectinload(Reviews.user)
            ))).scalars().all()
            reviews = [SReviewInfo.model_validate(result, from_attributes=True) for result in resp]
            return reviews
