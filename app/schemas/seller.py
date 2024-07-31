from typing import Optional

from pydantic import BaseModel, PositiveInt, EmailStr

from app.schemas.user import SUser


class SCompany(BaseModel):
    description: Optional[str] = None
    inn: Optional[int] = None
    payment_details: Optional[str] = None
    legal_address: Optional[str] = None
    passport_data: Optional[str] = None


class SCompanyAdd(SCompany):
    name: str


class SSellerCom(BaseModel):
    type_company: int


class SSellerAdd(SSellerCom):
    company_id: int
    user_id: int
    company_role: int


class SCompanyUpdate(SCompany):
    name: Optional[str] = None


class SProducts(BaseModel):
    name: str
    price: Optional[PositiveInt] = None


class SProductDelete(BaseModel):
    product_id: int


class SManagerSignUp(BaseModel):
    email: EmailStr
    fullname: str
    age: Optional[PositiveInt] = None


class SManagerAdd(SUser):
    hashed_password: str
    salt: str
    white_list_ip: Optional[str] = None
    is_active: bool = False


class SManagerSetPassword(BaseModel):
    password: str


class SToken(BaseModel):
    token: str
