import asyncio
from sqlite3 import IntegrityError

from fastapi import HTTPException

from app.db.models import Users
from app.repositories.crud import SQLAlchemyRepository
from app.schemas.user import SUserAdd, SUserInfo


class UsersService:
    def __init__(self):
        self.user_repo = SQLAlchemyRepository(model=Users)

    async def add_one(self, data):
        try:
            user_id = await self.user_repo.create(data=data.model_dump())
            return user_id
        except IntegrityError:
            raise HTTPException(
                status_code=401,
                detail='User with this email are exists'
            )

    async def find_one(self, filter_by: dict, schema=SUserInfo):
        user = await self.user_repo.read(filter_by=filter_by, schema=schema)
        return user

    async def update(self, filter_by: dict, update_value: dict):
        user_id = await self.user_repo.update(filter_by=filter_by, update_value=update_value)
        if not user_id:
            raise HTTPException(
                status_code=403,
                detail='User does not exist'
            )
