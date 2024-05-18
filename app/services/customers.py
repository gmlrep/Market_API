import asyncio
from sqlite3 import IntegrityError

from fastapi import HTTPException, UploadFile

from app.db.models import Users, Sellers, Companies, Products, Category, Contacts, Orders, Reviews, PhotoReview
from app.repositories.crud import SQLAlchemyRepository
from app.schemas.customer import SCategories, SBasket, SOrderId, SReviewAdd, SContact
from app.schemas.seller import SSellerCom, SCompanyAdd, SCompanyUpdate, SProducts, SSellerAdd
from app.schemas.user import SUserAdd, SUserInfo, SUserEdit


class CustomersService:
    def __init__(self):
        self.customer_repo = SQLAlchemyRepository(model=Users)
        self.product_repo = SQLAlchemyRepository(model=Products)
        self.category_repo = SQLAlchemyRepository(model=Category)
        self.contact_repo = SQLAlchemyRepository(model=Contacts)
        self.order_repo = SQLAlchemyRepository(model=Orders)
        self.review_repo = SQLAlchemyRepository(model=Reviews)
        self.photo_review_repo = SQLAlchemyRepository(model=PhotoReview)

    async def update_profile(self, data: SUserEdit, user_id: int, file: UploadFile):
        user_param = data.model_dump(exclude_none=True)
        if file is not None:
            user_param['photo'] = f'user{user_id}_1.jpg'
        if user_param == {}:
            raise HTTPException(
                status_code=403,
                detail='Do not update'
            )
        user_id = await self.customer_repo.update(filter_by={'id': user_id}, update_value=user_param)
        if not user_id:
            raise HTTPException(
                status_code=403,
                detail='User does not exist'
            )

    async def get_categories(self) -> list[SCategories]:
        categories = await self.category_repo.find_all(schema=SCategories)
        return categories

    async def add_basket(self, data: SBasket, user_id: int) -> int:
        contact_id = await self.contact_repo.find_id(filter_by={'user_id': user_id})
        order_param = data.model_dump(exclude_none=True)
        order_param.update(user_id=user_id)
        order_param.update(contact_id=contact_id) if contact_id else ...
        order_id = await self.order_repo.find_id(filter_by={'user_id': user_id, 'is_taken': False,
                                                            'is_order': False, 'product_id': data.product_id})
        if order_id:
            resp = await self.order_repo.update(filter_by={'id': order_id},
                                                update_value={'quantity': data.quantity})
            return resp
        resp = await self.order_repo.create(data=order_param)
        return resp

    async def delete_basket(self, data: SOrderId, user_id: int) -> int:
        order_id = await self.order_repo.delete(filter_by={'id': data.order_id, 'user_id': user_id,
                                                           'is_taken': False, 'is_order': False})
        if order_id is None:
            raise HTTPException(
                status_code=404,
                detail="Order by this id doesn't exist"
            )
        return order_id

    async def add_review(self, data: SReviewAdd, user_id: int, photos: list[UploadFile] | None = None) -> int:
        order_id = await self.order_repo.find_id(filter_by={'user_id': user_id, 'product_id': data.product_id,
                                                            'is_taken': True, 'is_order': True})
        if not order_id:
            raise HTTPException(
                status_code=404,
                detail='Order not found'
            )
        review_id = await self.review_repo.find_id(filter_by={'order_id': order_id})
        if review_id:
            raise HTTPException(
                status_code=403,
                detail='Review is already exist'
            )
        review_param = data.model_dump()
        review_param.update(user_id=user_id, order_id=order_id)
        review_ids = await self.review_repo.create(data=review_param)
        if photos:
            for i, photo in enumerate(photos):
                await self.photo_review_repo.create(data={'review_id': review_ids,
                                                          'photo': f'review{review_ids}_{i + 1}.jpg'})
        return review_ids

    async def add_contacts(self, data: SContact, user_id: int) -> int:
        contact_id = await self.contact_repo.find_id(filter_by={'user_id': user_id})
        if contact_id:
            raise HTTPException(
                status_code=403,
                detail='Contacts is already exist'
            )
        contact_param = data.model_dump()
        contact_param.update(user_id=user_id)
        resp = await self.contact_repo.create(data=contact_param)
        return resp

    async def edit_contacts(self, data: SContact, user_id: int) -> int:
        contact_id = await self.contact_repo.find_id(filter_by={'user_id': user_id})
        if not contact_id:
            raise HTTPException(
                status_code=404,
                detail='Contacts does not exist'
            )
        contact_param = data.model_dump()
        await self.contact_repo.update(filter_by={'user_id': user_id}, update_value=contact_param)
