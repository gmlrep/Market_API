from pydantic import BaseModel, constr, EmailStr, PositiveInt


class UserLogIn(BaseModel):
    username: str
    password: str


class SUser(BaseModel):
    email: EmailStr
    role: int = 1
    fullname: str
    age: PositiveInt


class SUserSignUp(SUser):
    password: constr(min_length=8, max_length=24)


class SUserAdd(SUser):
    hashed_password: str
    salt: str
    white_list_ip: str | None = None


class SUserInfo(SUser):
    id: int
    hashed_password: str
    salt: str
    is_active: bool
    is_enabled: bool
    is_baned: bool
    is_admin: bool
    white_list_ip: str | None = None


class STokenVerify(BaseModel):
    token: str


class HashedPasswordSalt(BaseModel):
    hashed_password: str
    salt: str


class SToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class SPasswordChange(BaseModel):
    current_password: str
    new_password: str


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
    age: PositiveInt | None = None
