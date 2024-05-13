from pydantic import BaseModel


class SCategoryAdd(BaseModel):
    name: str


class SUserId(BaseModel):
    user_id: int