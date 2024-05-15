from fastapi import UploadFile
from pydantic import BaseModel, Json, PositiveInt

from app.schemas.user import SUser


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


class SParameters(BaseModel):
    details: Json


class SProductDelete(BaseModel):
    product_id: int


class SManagerSignUp(SUser):
    fullname: str
    age: PositiveInt | None = None


class SManagerAdd(SUser):
    fullname: str
    age: PositiveInt
    role: int = 1
    hashed_password: str
    salt: str
    white_list_ip: str | None = None
    is_active: bool = False


class SManagerSetPassword(BaseModel):
    token: str
    password: str
