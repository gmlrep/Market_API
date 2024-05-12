from enum import Enum

from fastapi import UploadFile
from pydantic import BaseModel, constr, EmailStr

from app.schemas.user import SUser


class SSellerSignUp(SUser):
    fullname: str
    password: constr(min_length=8, max_length=24)


class SSellerAdd(SUser):
    fullname: str
    role: int = 2
    hashed_password: str
    salt: str
    white_list_ip: str


class SCompany(BaseModel):
    name: str
    description: str | None = None
    inn: int | None = None
    payment_details: str | None = None
    legal_address: str | None = None
    passport_data: str | None = None


class SSellerCom(BaseModel):
    type_company: int


class SCompanyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    inn: int | None = None
    payment_details: str | None = None
    legal_address: str | None = None
    passport_data: str | None = None


class SSellerId(BaseModel):
    user_id: int


class SProducts(BaseModel):
    name: str
    price: int | None = None