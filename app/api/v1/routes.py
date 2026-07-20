from fastapi import APIRouter

from app.api.v1.endpoints.auth import users
from app.api.v1.endpoints.customers import customers
from app.api.v1.endpoints.sellers import sellers

routers = APIRouter()
routers.include_router(users)
routers.include_router(customers)
routers.include_router(sellers)
