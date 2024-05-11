from fastapi import HTTPException
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError

from app.db.database import Base
from app.db.models import User, Tasks
from app.schemas.task import STask, SUserTask
from app.schemas.user import SUserAdd, SUserInfo
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
    async def add_user(cls, data: SUserAdd) -> int:
        async with async_session() as session:
            user_param = data.model_dump()
            user = User(**user_param)
            try:
                session.add(user)
                await session.flush()
                await session.commit()
                return user.user_id

            except IntegrityError:
                raise HTTPException(
                    status_code=401,
                    detail='User with this username or email are exists'
                )

    @classmethod
    async def get_user(cls, username: str) -> SUserInfo | bool:
        async with async_session() as session:
            response = await session.execute(select(User).filter_by(username=username))
            resp = response.first()
            if not resp:
                return False
            user = [SUserInfo.model_validate(result, from_attributes=True) for result in resp]
            return user[0]

    @classmethod
    async def add_task(cls, data: STask, user_id: int, is_shared: bool = False) -> bool:
        async with async_session() as session:
            task_param = data.model_dump()
            task = Tasks(title=data.title, user_id=user_id, is_shared=is_shared)
            session.add(task)
            await session.flush()
            await session.commit()
            return True

    @classmethod
    async def get_tasks(cls, user_id, is_shared: bool = False) -> list[SUserTask]:
        async with async_session() as session:
            response = await session.execute(select(Tasks).filter_by(user_id=user_id, is_shared=is_shared))
            resp = response.scalars().all()
            tasks = [SUserTask.model_validate(result, from_attributes=True) for result in resp]
            return tasks

    @classmethod
    async def delete_user_task_by_id(cls, user_id, task_id) -> bool:
        async with async_session() as session:
            data = await session.execute(delete(Tasks).filter_by(user_id=user_id, id=task_id).returning(Tasks.id))
            if data.scalar() is None:
                raise HTTPException(
                    status_code=404,
                    detail='Not Found this task'
                )
            await session.commit()
            return True

    @classmethod
    async def update_task_by_id(cls, user_id: int, status: bool, task_id: int) -> None:
        async with async_session() as session:
            data = await session.execute(update(Tasks).
                                         where(Tasks.user_id == user_id, Tasks.id == task_id).
                                         values(done=status).returning(Tasks.id))
            if data.scalar() is None:
                raise HTTPException(
                    status_code=404,
                    detail='Not Found this task'
                )
            await session.commit()
