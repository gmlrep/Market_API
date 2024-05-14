from pydantic import BaseModel


class SCategoryAdd(BaseModel):
    name: str


class SBanedUser(BaseModel):
    user_id: int
    is_baned: bool


class SCategoryDelete(BaseModel):
    name: str | None = None
    id: int | None = None
