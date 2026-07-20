from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models import (
    Users,
    Category,
    Contacts,
    Orders,
    Reviews,
    PhotoReview,
)
from app.repository.base import BaseRepository, SessionFactory
from app.schemas.customer import SAccountInfo, SProduct, SReviewInfo


class CategoryRepository(BaseRepository):
    def __init__(self, session: SessionFactory):
        super().__init__(session=session, model=Category)


class ContactRepository(BaseRepository):
    def __init__(self, session: SessionFactory):
        super().__init__(session=session, model=Contacts)


class OrderRepository(BaseRepository):
    def __init__(self, session: SessionFactory):
        super().__init__(session=session, model=Orders)


class ReviewRepository(BaseRepository):
    def __init__(self, session: SessionFactory):
        super().__init__(session=session, model=Reviews)

    async def get_by_product(self, param: SProduct) -> list[SReviewInfo]:
        async with self.session() as session:
            resp = (
                (
                    await session.execute(
                        select(Reviews)
                        .filter_by(product_id=param.product_id)
                        .options(
                            selectinload(Reviews.photo),
                            selectinload(Reviews.user),
                        )
                    )
                )
                .scalars()
                .all()
            )
            return [
                SReviewInfo.model_validate(result, from_attributes=True) for result in resp
            ]


class PhotoReviewRepository(BaseRepository):
    def __init__(self, session: SessionFactory):
        super().__init__(session=session, model=PhotoReview)


class CustomerRepository(BaseRepository):
    """User-facing customer queries (account with relations)."""

    def __init__(self, session: SessionFactory):
        super().__init__(session=session, model=Users)

    async def get_account_info(self, user_id: int) -> SAccountInfo:
        async with self.session() as session:
            user = (
                await session.execute(
                    select(Users)
                    .filter_by(id=user_id)
                    .options(selectinload(Users.order), selectinload(Users.contact))
                )
            ).scalars().first()
            if user is None:
                raise NotFoundError(detail="User not found")
            return SAccountInfo.model_validate(user, from_attributes=True)
