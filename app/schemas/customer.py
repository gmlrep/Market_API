from datetime import datetime

from pydantic import BaseModel, PositiveInt


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
    photos: str
    price: PositiveInt | None = None
    quantity: PositiveInt | None = None
    rate: int | None = None


class SAccountInfo(BaseModel):
    id: int
    email: str
    fullname: str
    age: PositiveInt
    photo: str
    create_at: datetime


class SOrderId(BaseModel):
    order_id: int


class SCategories(BaseModel):
    id: int
    name: str


class SBasket(BaseModel):
    product_id: int
    quantity: PositiveInt


# rep = {
#     'id': 1,
#     'email': 'erfg',
#     "parameters":
#         [
#             {'size': 2,
#              'height': 10
#              }
#         ]
# }
