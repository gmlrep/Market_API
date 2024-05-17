from typing import Union

from fastapi import APIRouter, Response, Request, HTTPException
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse

from app.core.config import settings
from app.core.security import authenticate_user, create_refresh_token, create_access_token, is_access_token, \
    is_access_token_admin
from app.db.database import async_session
from app.core.redis_client import Redis


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:

        form = await request.form()
        email, password = form['username'], form['password']

        async with async_session() as session:
            user = await authenticate_user(email, password)

            if user.is_admin is True:
                payload = {'sub': user.id, 'role': user.role, 'is_active': user.is_active,
                           'is_admin': user.is_admin, 'is_baned': user.is_baned}
                access_token = create_access_token(data=payload)
                refresh_token = create_refresh_token(data=payload)
                request.session.update({'access_token': access_token, 'token_type': 'Bearer'})
                await Redis.set(request.client.host, refresh_token,
                                60 * 60 * 24 * settings.auth_jwt.refresh_token_expire_days)
                return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        await Redis.delete(request.client.host)
        return True

    async def authenticate(self, request: Request) -> Union[Response, bool]:
        token = request.session.get("access_token")
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        payload = await is_access_token_admin(token=token, request=request)
        is_admin = payload.get('is_admin')
        if not is_admin:
            raise HTTPException(
                status_code=406,
                detail='Do not permission'
            )
        return True


auth_backend = AdminAuth(secret_key='admin')
