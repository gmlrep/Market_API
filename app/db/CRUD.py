import asyncio

from fastapi import HTTPException
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError

from app.db.database import Base
from app.db.models import Users, Sellers, Companies, Products, Category, Parameters
from app.schemas.admin import SCategoryAdd
from app.schemas.seller import SSellerAdd, SCompany, SSellerCom, SCompanyUpdate, SSellerId, SProducts
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

    @classmethod
    async def add_user(cls, data: SUserAdd | SSellerAdd) -> int:
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
    async def edit_profile_user(cls, param: SUserEdit, user_id: int):
        async with async_session() as session:
            user_param = {key: value for key, value in param.model_dump().items() if value is not None}
            if user_param == {}:
                return
            await session.execute(update(Users).filter_by(id=user_id).values(**user_param))
            await session.commit()

    @classmethod
    async def add_product_seller(cls, param: SProducts, user_id: int, categories: str, details: dict):
        async with async_session() as session:
            company_id = (await session.execute(select(Sellers.company_id).filter_by(user_id=user_id))).scalar()
            categories_id = await session.execute(select(Category.id).filter_by(name=categories))
            prodict_param = param.model_dump()
            prodict_param.update(company_id=company_id, category_id=categories_id)
            product = Products(**prodict_param)
            await session.commit()
            if details is not None:
                for detail in details:
                    parameters = Parameters(**detail)

    @classmethod
    async def add_category(cls, param: SCategoryAdd):
        async with async_session() as session:
            category_param = param.model_dump()
            category = Category(**category_param)
            await session.commit()




    # @classmethod
    # async def add_task(cls, data: STask, user_id: int, is_shared: bool = False) -> bool:
    #     async with async_session() as session:
    #         task_param = data.model_dump()
    #         task = Tasks(title=data.title, user_id=user_id, is_shared=is_shared)
    #         session.add(task)
    #         await session.flush()
    #         await session.commit()
    #         return True
    #
    # @classmethod
    # async def get_tasks(cls, user_id, is_shared: bool = False) -> list[SUserTask]:
    #     async with async_session() as session:
    #         response = await session.execute(select(Tasks).filter_by(user_id=user_id, is_shared=is_shared))
    #         resp = response.scalars().all()
    #         tasks = [SUserTask.model_validate(result, from_attributes=True) for result in resp]
    #         return tasks
    #
    # @classmethod
    # async def delete_user_task_by_id(cls, user_id, task_id) -> bool:
    #     async with async_session() as session:
    #         data = await session.execute(delete(Tasks).filter_by(user_id=user_id, id=task_id).returning(Tasks.id))
    #         if data.scalar() is None:
    #             raise HTTPException(
    #                 status_code=404,
    #                 detail='Not Found this task'
    #             )
    #         await session.commit()
    #         return True
    #
    # @classmethod
    # async def update_task_by_id(cls, user_id: int, status: bool, task_id: int) -> None:
    #     async with async_session() as session:
    #         data = await session.execute(update(Tasks).
    #                                      where(Tasks.user_id == user_id, Tasks.id == task_id).
    #                                      values(done=status).returning(Tasks.id))
    #         if data.scalar() is None:
    #             raise HTTPException(
    #                 status_code=404,
    #                 detail='Not Found this task'
    #             )
    #         await session.commit()
