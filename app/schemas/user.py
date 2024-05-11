from enum import Enum

from pydantic import BaseModel, constr, EmailStr


class UserRole(str, Enum):
    users = 'users'
    admin = 'admin'


class SUser(BaseModel):
    username: constr(min_length=4)
    email: EmailStr


class SUserSignUp(SUser):
    password: constr(min_length=8, max_length=24)


class SUserAdd(SUser):
    hashed_password: str
    salt: str
    white_list_ip: str


class SUserInfo(SUser):
    role: UserRole | None = None
    user_id: int
    hashed_password: str
    salt: str


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
