from datetime import datetime

from pydantic import BaseModel


class SCategory(BaseModel):
    category: str


class SProduct(BaseModel):
    product_id: int


class SParameters(BaseModel):
    parameters: list[dict]


class SProductsInfo(BaseModel):
    id: int
    name: str
    category_id: int
    company_id: int
    # photos_id: list[int]
    price: int | None = None
    quantity: int | None = None
    rate: int | None = None


class SAccountInfo(BaseModel):
    id: int
    email: str
    fullname: str
    age: int
    create_at: datetime


rep = {
    'id': 1,
    'email': 'erfg',
    "parameters":
        [
            {'size': 2,
             'height': 10
             }
        ]
}
