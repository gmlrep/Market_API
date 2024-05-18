import asyncio

from pydantic import BaseModel
from sqlalchemy import insert, select, update, delete

from app.db.database import async_session, Base
from app.db.models import Users
from app.schemas.user import SUserAdd


class SQLAlchemyRepository:
    def __init__(self, model):
        self.model = model

    async def create(self, data: dict) -> int:
        async with async_session() as session:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            resp = await session.execute(stmt)
            await session.commit()
            return resp.scalar_one()

    async def read(self, schema, filter_by: dict):
        async with async_session() as session:
            stmt = select(self.model).filter_by(**filter_by)
            resp = await session.execute(stmt)
            res = [schema.model_validate(result, from_attributes=True) for result in resp.first()]
            return res[0]

    async def update(self, filter_by: dict, update_value: dict):
        async with async_session() as session:
            stmt = update(self.model).filter_by(**filter_by).values(**update_value).returning(self.model.id)
            resp = await session.execute(stmt)
            await session.commit()
            return resp.scalar_one_or_none()

    async def delete(self, filter_by: dict) -> int:
        async with async_session() as session:
            stmt = delete(self.model).filter_by(**filter_by).returning(self.model.id)
            resp = await session.execute(stmt)
            await session.commit()
            return resp

    async def find_id(self, filter_by: dict) -> int:
        async with async_session() as session:
            stmt = select(self.model.id).filter_by(**filter_by)
            resp = await session.execute(stmt)
            return resp.scalar_one_or_none()

    async def find_all(self, schema):
        async with async_session() as session:
            stmt = select(self.model)
            resp = await session.execute(stmt)
            res = [schema.model_validate(result, from_attributes=True) for result in resp.scalars().all()]
            return res

    async def update_company(self, filter_by: dict, values: dict, sub_model):
        async with async_session() as session:
            stmt = update(self.model).where(
                self.model.id == (select(sub_model.company_id).filter_by(**filter_by)).scalar_subquery()
            ).values(**values).returning(self.model.id)
            resp = await session.execute(stmt)
            await session.commit()
            return resp
