from enum import Enum

from pydantic import BaseModel, constr, EmailStr


class SUser(BaseModel):
    email: EmailStr


class SUserSignUp(SUser):
    role: int = 1
    fullname: str
    age: int
    password: constr(min_length=8, max_length=24)


class SUserAdd(SUser):
    fullname: str
    age: int
    role: int = 1
    hashed_password: str
    salt: str
    white_list_ip: str


class SUserInfo(SUser):
    role: int
    id: int
    hashed_password: str
    salt: str
    is_active: bool
    is_enabled: bool
    is_admin: bool


class SToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class STokenResponse(BaseModel):
    status: str = 'success'
    data: SToken | None = None
    details: str | None = None


class SOkResponse(BaseModel):
    status: str = 'success'
    data: dict = {'ok': True}
    details: str | None = None


class SUserEdit(BaseModel):
    fullname: str | None = None
    age: int | None = None

