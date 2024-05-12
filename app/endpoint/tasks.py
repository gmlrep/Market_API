from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect

from app.core.security import is_refresh_token, access_admin, decode_jwt, is_valid_token
from app.db.CRUD import BaseCRUD
from app.schemas.task import STask, SUserTask
from app.schemas.user import SOkResponse

tasks = APIRouter(
    prefix="/api/v1/tasks",
    tags=['tasks'],
    dependencies=[Depends(access_admin)]
)


# async def get_task_list(websocket: WebSocket, user_id: int):
#     tasks_shared = await ClientDB.get_tasks(user_id=user_id, is_shared=True)
#     for task in tasks_shared:
#         print(task)
#         await websocket.send_text(str(task))

# websocket_clients = []


@tasks.post('/', status_code=201, dependencies=[Depends(access_admin)])
async def create_task(param: Annotated[STask, Depends()], request: Request, websocket: WebSocket = None) -> SOkResponse:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    # username = payload.get('username')
    await BaseCRUD.add_task(data=param, user_id=user_id, is_shared=param.is_shared)
    # if param.is_shared:
    #     for client in websocket_clients:
    #         await websocket.send_text(f'Пользователь {username} добавил задание - {param.title}')
    #         await get_task_list(user_id=user_id, websocket=websocket)
    return SOkResponse()


@tasks.get('/', dependencies=[Depends(access_admin)])
async def get_user_tasks(request: Request) -> list[SUserTask]:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    task_list = await BaseCRUD.get_tasks(user_id=user_id)
    return task_list


@tasks.delete('/delete_task', dependencies=[Depends(access_admin)])
async def delete_user_task(task_id: int, request: Request) -> SOkResponse:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    await BaseCRUD.delete_user_task_by_id(user_id=user_id, task_id=task_id)
    return SOkResponse()


@tasks.patch('/update_task_status', dependencies=[Depends(access_admin)])
async def update_user_task(task_id: int, status: bool, request: Request) -> SOkResponse:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    await BaseCRUD.update_task_by_id(user_id=user_id, task_id=task_id, status=status)
    return SOkResponse()


# @tasks.websocket('/task_board')
# async def websocket_board(websocket: WebSocket):
#     await websocket.accept()
#     await websocket.send_text('Enter your jwt token')
#     token = await websocket.receive_text()
#     status = is_valid_token(token)
#     if not status:
#         await websocket.close(code=1008)
#         return
#     websocket_clients.append(websocket)
#
#     try:
#         while True:
#             await websocket.receive_text()
#             await get_task_list(websocket, user_id=1)
#     except WebSocketDisconnect:
#         websocket_clients.remove(websocket)
