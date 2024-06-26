from pydantic import BaseModel, PositiveInt, EmailStr

from app.schemas.user import SUser


class SCompany(BaseModel):
    description: str | None = None
    inn: int | None = None
    payment_details: str | None = None
    legal_address: str | None = None
    passport_data: str | None = None


class SCompanyAdd(SCompany):
    name: str


class SSellerCom(BaseModel):
    type_company: int


class SSellerAdd(SSellerCom):
    company_id: int
    user_id: int
    company_role: int


class SCompanyUpdate(SCompany):
    name: str | None = None


class SProducts(BaseModel):
    name: str
    price: PositiveInt | None = None


class SProductDelete(BaseModel):
    product_id: int


class SManagerSignUp(BaseModel):
    email: EmailStr
    fullname: str
    age: PositiveInt | None = None


class SManagerAdd(SUser):
    hashed_password: str
    salt: str
    white_list_ip: str | None = None
    is_active: bool = False


class SManagerSetPassword(BaseModel):
    password: str


class SToken(BaseModel):
    token: str
