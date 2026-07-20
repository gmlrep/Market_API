from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import TypeVar, Type, Any

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func, delete, update, select, insert
from sqlalchemy.exc import IntegrityError

from app.core.database import Base
from app.core.config import settings
from app.utils.query_builder import dict_to_sclachemy_filter_options
from app.core.exceptions import NotFoundError, DuplicateError

ModelType = TypeVar("ModelType", bound=Base)
SessionFactory = Callable[..., AbstractAsyncContextManager[AsyncSession]]


class BaseRepository:
    def __init__(self, session: SessionFactory, model: Type[ModelType]) -> None:
        self.session = session
        self.model = model

    async def read_by_options(
        self, schema: PydanticBaseModel, eager: bool = False
    ) -> dict[str, Any]:
        async with self.session() as session:
            schema_as_dict = schema.model_dump(exclude_none=True)
            ordering: str = schema_as_dict.get("ordering", settings.database.ORDERING)
            order_query = (
                getattr(self.model, ordering[1:]).desc()
                if ordering.startswith("-")
                else getattr(self.model, ordering).asc()
            )
            page = schema_as_dict.get("page", settings.database.PAGE)
            page_size = schema_as_dict.get("page_size", settings.database.PAGE_SIZE)
            filter_options = dict_to_sclachemy_filter_options(
                self.model, schema.model_dump(exclude_none=True)
            )
            stmt = select(self.model)
            if eager:
                for relation in getattr(self.model, "eagers", []):
                    stmt = stmt.options(selectinload(getattr(self.model, relation)))
            stmt = stmt.filter(filter_options)
            stmt = stmt.order_by(order_query)
            if page_size == "all":
                result = await session.scalars(stmt)
                rows = result.all()
            else:
                stmt = stmt.limit(page_size).offset((page - 1) * page_size)
                result = await session.scalars(stmt)
                rows = result.all()
            total_count = await session.scalar(
                select(func.count()).select_from(select(self.model).filter(filter_options).subquery())
            )
            return {
                "founds": rows,
                "search_options": {
                    "page": page,
                    "page_size": page_size,
                    "ordering": ordering,
                    "total_count": total_count,
                },
            }

    async def read_by_id(self, id: int, eager: bool = False) -> Any:
        async with self.session() as session:
            stmt = select(self.model)
            if eager:
                for relation in getattr(self.model, "eagers", []):
                    stmt = stmt.options(selectinload(getattr(self.model, relation)))
            stmt = stmt.filter(self.model.id == id)
            result = await session.scalars(stmt)
            query = result.first()
            if not query:
                raise NotFoundError(detail=f"not found id: {id}")
            return query

    async def create(self, schema: PydanticBaseModel | dict) -> Any:
        async with self.session() as session:
            sc = schema.model_dump(exclude_none=True) if hasattr(schema, "model_dump") else schema
            stmt = insert(self.model).values(sc).returning(self.model)
            try:
                result = await session.scalars(stmt)
                await session.commit()
                return result.first()
            except IntegrityError as e:
                await session.rollback()
                if getattr(e.orig, "sqlstate", None) == "23505":
                    raise DuplicateError(detail=f"duplicate data: {e.orig}")
                raise

    async def create_returning_id(self, data: dict) -> int:
        row = await self.create(data)
        return row.id

    async def update_by_id(self, id: int, schema: PydanticBaseModel | dict) -> Any:
        async with self.session() as session:
            values = schema.model_dump(exclude_none=True) if hasattr(schema, "model_dump") else schema
            stmt = update(self.model).where(self.model.id == id).values(values)
            try:
                await session.execute(stmt)
                await session.commit()
                return await self.read_by_id(id)
            except Exception:
                raise NotFoundError(detail=f"not found id: {id}")

    async def update_attr(self, id: int, collumn: str, value: Any) -> Any:
        async with self.session() as session:
            stmt = update(self.model).where(self.model.id == id).values({collumn: value})
            try:
                await session.execute(stmt)
                await session.commit()
                return await self.read_by_id(id)
            except Exception:
                raise NotFoundError(detail=f"not found id: {id}")

    async def whole_update(self, id: int, schema: PydanticBaseModel) -> Any:
        return await self.update_by_id(id, schema)

    async def delete_by_id(self, id: int) -> None:
        async with self.session() as session:
            stmt = delete(self.model).where(self.model.id == id)
            try:
                await session.execute(stmt)
                await session.commit()
            except Exception:
                raise NotFoundError(detail=f"not found id: {id}")

    async def find_one(self, filter_by: dict, schema: type[PydanticBaseModel] | None = None):
        async with self.session() as session:
            stmt = select(self.model).filter_by(**filter_by)
            result = (await session.execute(stmt)).scalars().first()
            if result is None:
                return None
            if schema is not None:
                return schema.model_validate(result, from_attributes=True)
            return result

    async def find_id(self, filter_by: dict) -> int | None:
        async with self.session() as session:
            stmt = select(self.model.id).filter_by(**filter_by)
            resp = await session.execute(stmt)
            return resp.scalar_one_or_none()

    async def find_all(self, schema: type[PydanticBaseModel] | None = None):
        async with self.session() as session:
            stmt = select(self.model)
            resp = await session.execute(stmt)
            rows = resp.scalars().all()
            if schema is not None:
                return [schema.model_validate(result, from_attributes=True) for result in rows]
            return rows

    async def update_by_filter(self, filter_by: dict, update_value: dict) -> int | None:
        async with self.session() as session:
            stmt = (
                update(self.model)
                .filter_by(**filter_by)
                .values(**update_value)
                .returning(self.model.id)
            )
            resp = await session.execute(stmt)
            await session.commit()
            return resp.scalar_one_or_none()

    async def delete_by_filter(self, filter_by: dict) -> int | None:
        async with self.session() as session:
            stmt = delete(self.model).filter_by(**filter_by).returning(self.model.id)
            resp = await session.execute(stmt)
            await session.commit()
            return resp.scalar_one_or_none()

    async def close_scope_session(self) -> None:
        async with self.session() as session:
            await session.close()
