from fastapi import UploadFile
from pydantic import BaseModel


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
    details: dict
