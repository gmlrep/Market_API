from fastapi import HTTPException, UploadFile

from app.repository.customer import (
    CustomerRepository,
    CategoryRepository,
    ContactRepository,
    OrderRepository,
    ReviewRepository,
    PhotoReviewRepository,
)
from app.repository.seller import ProductRepository
from app.schemas.customer import (
    SCategories,
    SBasket,
    SOrderId,
    SReviewAdd,
    SContact,
    SProductsInfo,
    SAccountInfo,
    SProduct,
    SReviewInfo,
)
from app.schemas.user import SUserEdit
from app.services.base import BaseService


class CustomersService(BaseService):
    def __init__(
        self,
        customer_repository: CustomerRepository,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
        contact_repository: ContactRepository,
        order_repository: OrderRepository,
        review_repository: ReviewRepository,
        photo_review_repository: PhotoReviewRepository,
    ):
        super().__init__(repository=customer_repository)
        self.customer_repository = customer_repository
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.contact_repository = contact_repository
        self.order_repository = order_repository
        self.review_repository = review_repository
        self.photo_review_repository = photo_review_repository

    async def update_profile(self, data: SUserEdit, user_id: int, file: UploadFile | None):
        user_param = data.model_dump(exclude_none=True)
        if file is not None:
            user_param["photo"] = f"user{user_id}_1.jpg"
        if not user_param:
            raise HTTPException(status_code=403, detail="Do not update")
        updated = await self.customer_repository.update_by_filter(
            filter_by={"id": user_id}, update_value=user_param
        )
        if not updated:
            raise HTTPException(status_code=403, detail="User does not exist")

    async def get_categories(self) -> list[SCategories]:
        return await self.category_repository.find_all(schema=SCategories)

    async def get_products_by_category(self, category_name: str) -> list[SProductsInfo]:
        return await self.product_repository.get_by_category_name(category_name)

    async def get_product(self, product_id: int) -> SProductsInfo:
        return await self.product_repository.get_product_info(product_id)

    async def get_account(self, user_id: int) -> SAccountInfo:
        return await self.customer_repository.get_account_info(user_id)

    async def get_reviews(self, param: SProduct) -> list[SReviewInfo]:
        return await self.review_repository.get_by_product(param)

    async def add_basket(self, data: SBasket, user_id: int) -> int:
        contact_id = await self.contact_repository.find_id(filter_by={"user_id": user_id})
        order_param = data.model_dump(exclude_none=True)
        order_param["user_id"] = user_id
        if contact_id:
            order_param["contact_id"] = contact_id
        order_id = await self.order_repository.find_id(
            filter_by={
                "user_id": user_id,
                "is_taken": False,
                "is_order": False,
                "product_id": data.product_id,
            }
        )
        if order_id:
            return await self.order_repository.update_by_filter(
                filter_by={"id": order_id},
                update_value={"quantity": data.quantity},
            )
        row = await self.order_repository.create(order_param)
        return row.id

    async def delete_basket(self, data: SOrderId, user_id: int) -> int:
        order_id = await self.order_repository.delete_by_filter(
            filter_by={
                "id": data.order_id,
                "user_id": user_id,
                "is_taken": False,
                "is_order": False,
            }
        )
        if order_id is None:
            raise HTTPException(
                status_code=404,
                detail="Order by this id doesn't exist",
            )
        return order_id

    async def add_review(
        self, data: SReviewAdd, user_id: int, photos: list[UploadFile] | None = None
    ) -> int:
        order_id = await self.order_repository.find_id(
            filter_by={
                "user_id": user_id,
                "product_id": data.product_id,
                "is_taken": True,
                "is_order": True,
            }
        )
        if not order_id:
            raise HTTPException(status_code=404, detail="Order not found")
        review_id = await self.review_repository.find_id(filter_by={"order_id": order_id})
        if review_id:
            raise HTTPException(status_code=403, detail="Review is already exist")
        review_param = data.model_dump()
        review_param.update(user_id=user_id, order_id=order_id)
        review = await self.review_repository.create(review_param)
        if photos:
            for i, _photo in enumerate(photos):
                await self.photo_review_repository.create(
                    {"review_id": review.id, "photo": f"review{review.id}_{i + 1}.jpg"}
                )
        return review.id

    async def add_contacts(self, data: SContact, user_id: int) -> int:
        contact_id = await self.contact_repository.find_id(filter_by={"user_id": user_id})
        if contact_id:
            raise HTTPException(status_code=403, detail="Contacts is already exist")
        contact_param = data.model_dump()
        contact_param["user_id"] = user_id
        row = await self.contact_repository.create(contact_param)
        return row.id

    async def edit_contacts(self, data: SContact, user_id: int) -> None:
        contact_id = await self.contact_repository.find_id(filter_by={"user_id": user_id})
        if not contact_id:
            raise HTTPException(status_code=404, detail="Contacts does not exist")
        await self.contact_repository.update_by_filter(
            filter_by={"user_id": user_id}, update_value=data.model_dump()
        )
