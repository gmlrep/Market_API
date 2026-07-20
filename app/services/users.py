from app.core.exceptions import DuplicateError, AuthError, UnauthorizedError
from app.repository.user import UserRepository
from app.schemas.user import SUserAdd, SUserInfo
from app.services.base import BaseService


class UsersService(BaseService):
    def __init__(self, user_repository: UserRepository):
        super().__init__(repository=user_repository)
        self.user_repository = user_repository

    async def add_one(self, data: SUserAdd) -> int:
        try:
            user = await self.user_repository.create(data.model_dump())
            return user.id
        except DuplicateError:
            raise UnauthorizedError(detail="User with this email are exists")

    async def find_one(self, filter_by: dict, schema=SUserInfo):
        return await self.user_repository.find_one(filter_by=filter_by, schema=schema)

    async def update(self, filter_by: dict, update_value: dict):
        user_id = await self.user_repository.update_by_filter(
            filter_by=filter_by, update_value=update_value
        )
        if not user_id:
            raise AuthError(detail="User does not exist")
        return user_id
