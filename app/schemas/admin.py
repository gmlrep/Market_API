from pydantic import BaseModel


class SCategoryAdd(BaseModel):
    name: str
