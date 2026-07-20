from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, Response
from fastapi.requests import Request
import prometheus_client

from app.core.container import Container
from app.core.dependencies import get_user_id_by_token, get_user_id_by_set_token
from app.core.middleware.inject import inject
from app.core.security import get_hashed_psw
from app.processes.processes import send_verify_email, send_email_new_ip
from app.schemas.seller import SManagerSetPassword
from app.schemas.user import (
    SToken,
    STokenResponse,
    SOkResponse,
    SPasswordChange,
    UserLogIn,
)
from app.services.auth import AuthService

users = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

register_count = prometheus_client.Counter("register_count", "Number of register")


@users.post("/register", status_code=201)
@inject
async def registration(
    user=Depends(get_hashed_psw),
    auth_service: Annotated[AuthService, Depends(Provide[Container.auth_service])] = None,
) -> SOkResponse:
    register_count.inc(1)
    user_id = await auth_service.register(user)
    send_verify_email.delay(user_id=user_id, email=user.email)
    return SOkResponse()


@users.post("/login")
@inject
async def get_token(
    param: Annotated[UserLogIn, Depends()],
    response: Response,
    request: Request,
    auth_service: Annotated[AuthService, Depends(Provide[Container.auth_service])] = None,
) -> STokenResponse:
    access_token, user = await auth_service.login(
        email=param.username, password=param.password, request=request, response=response
    )
    if request.client.host not in (user.white_list_ip or ""):
        send_email_new_ip.delay(
            user_id=user.id, email=user.email, request_ip=request.client.host
        )
    return STokenResponse(data=SToken(access_token=access_token))


@users.post("/refresh")
@inject
async def auth_refresh_jwt(
    request: Request,
    response: Response,
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    auth_service: Annotated[AuthService, Depends(Provide[Container.auth_service])] = None,
) -> STokenResponse:
    access_token = await auth_service.refresh(
        user_id=user_id, request=request, response=response
    )
    return STokenResponse(data=SToken(access_token=access_token))


@users.post("/logout")
@inject
async def logout_user(
    response: Response,
    request: Request,
    auth_service: Annotated[AuthService, Depends(Provide[Container.auth_service])] = None,
) -> SOkResponse:
    await auth_service.logout(request=request, response=response)
    return SOkResponse()


@users.post("/delete_account")
@inject
async def delete_account(
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(Provide[Container.auth_service])] = None,
) -> SOkResponse:
    await auth_service.delete_account(user_id=user_id, request=request, response=response)
    return SOkResponse()


@users.post("/token")
@inject
async def set_password_by_manager(
    param: Annotated[SManagerSetPassword, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_set_token)],
    auth_service: Annotated[AuthService, Depends(Provide[Container.auth_service])] = None,
) -> SOkResponse:
    await auth_service.set_manager_password(user_id=user_id, password=param.password)
    return SOkResponse()


@users.post("/password")
@inject
async def change_password(
    param: Annotated[SPasswordChange, Depends()],
    user_id: Annotated[int, Depends(get_user_id_by_token)],
    response: Response,
    request: Request,
    auth_service: Annotated[AuthService, Depends(Provide[Container.auth_service])] = None,
) -> SOkResponse:
    await auth_service.change_password(
        user_id=user_id,
        current_password=param.current_password,
        new_password=param.new_password,
        request=request,
        response=response,
    )
    return SOkResponse()


@users.post("/email")
@inject
async def verify_user_email(
    user_id: Annotated[int, Depends(get_user_id_by_set_token)],
    auth_service: Annotated[AuthService, Depends(Provide[Container.auth_service])] = None,
) -> SOkResponse:
    await auth_service.verify_email(user_id=user_id)
    return SOkResponse()
