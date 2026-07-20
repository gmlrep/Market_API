from app.core.config import settings
from app.core.exceptions import AuthError
from app.core.redis_client import Redis
from app.core.security import (
    verify_password,
    set_update_tokens,
    decode_jwt,
    generate_salt,
    get_password_hash,
    get_changed_hashed_password,
)
from app.schemas.user import SUserInfo, SUserAdd
from app.services.base import BaseService
from app.services.users import UsersService
from fastapi import Request, Response, HTTPException


class AuthService(BaseService):
    def __init__(self, user_service: UsersService):
        super().__init__(repository=user_service.user_repository)
        self.user_service = user_service

    async def register(self, user: SUserAdd) -> int:
        return await self.user_service.add_one(user)

    async def authenticate(self, email: str, password: str) -> SUserInfo:
        user = await self.user_service.find_one({"email": email})
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(
            plain_password=password + user.salt + settings.password_salt.salt_static,
            hashed_password=user.hashed_password,
        ):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
            )
        return user

    async def login(
        self, email: str, password: str, request: Request, response: Response
    ) -> tuple[str, SUserInfo]:
        user = await self.authenticate(email=email, password=password)
        token = await set_update_tokens(user=user, request=request, response=response)
        return token, user

    async def refresh(self, user_id: int, request: Request, response: Response) -> str:
        payload = decode_jwt(token=await Redis.get(request.client.host))
        if payload.get("type") == "access":
            raise AuthError(detail="Incorrect refresh token")
        user = await self.user_service.find_one(filter_by={"id": user_id})
        return await set_update_tokens(user=user, request=request, response=response)

    async def logout(self, request: Request, response: Response) -> None:
        response.delete_cookie("access_token")
        await Redis.delete(request.client.host)

    async def delete_account(self, user_id: int, request: Request, response: Response) -> None:
        await self.user_service.update(
            filter_by={"id": user_id}, update_value={"is_active": False}
        )
        await Redis.delete(request.client.host)
        response.delete_cookie("access_token")

    async def set_manager_password(self, user_id: int, password: str) -> None:
        salt = generate_salt()
        hashed_password = get_password_hash(password=password + salt)
        await self.user_service.update(
            filter_by={"id": user_id},
            update_value={
                "hashed_password": hashed_password,
                "salt": salt,
                "is_active": True,
                "is_enabled": True,
            },
        )

    async def change_password(
        self, user_id: int, current_password: str, new_password: str, request: Request, response: Response
    ) -> None:
        user = await self.user_service.find_one(filter_by={"id": user_id})
        if not verify_password(
            plain_password=current_password + user.salt + settings.password_salt.salt_static,
            hashed_password=user.hashed_password,
        ):
            raise AuthError(detail="Current password incorrect")
        param = get_changed_hashed_password(new_password=new_password)
        await self.user_service.update(filter_by={"id": user_id}, update_value=param.model_dump())
        await set_update_tokens(user=user, request=request, response=response)

    async def verify_email(self, user_id: int) -> None:
        await self.user_service.update(
            filter_by={"id": user_id}, update_value={"is_enabled": True}
        )
