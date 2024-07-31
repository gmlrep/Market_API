from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt


class SCategory(BaseModel):
    category: str


class SProduct(BaseModel):
    product_id: int


class SParameters(BaseModel):
    name: str
    description: str


class SPhotos(BaseModel):
    photo: str


class SProductsInfo(BaseModel):
    id: int
    name: str
    category_id: int
    company_id: int
    photo: list[SPhotos]
    parameter: list[SParameters]
    price: Optional[PositiveInt] = None
    quantity: Optional[PositiveInt] = None
    rate: Optional[int] = None


class SContact(BaseModel):
    city: Optional[str] = None
    street: Optional[str] = None
    house: Optional[str] = None
    building: Optional[str] = None
    literal: Optional[str] = None
    apartment: Optional[str] = None


class SOrderInfo(BaseModel):
    id: int
    product_id: int
    quantity: int
    is_taken: bool
    is_order: bool


class SAccountInfo(BaseModel):
    id: int
    email: str
    fullname: str
    age: PositiveInt
    contact: Optional[SContact]
    order: list[SOrderInfo]
    photo: Optional[str]
    create_at: datetime


class SOrderId(BaseModel):
    order_id: int


class SCategories(BaseModel):
    id: int
    name: str


class SBasket(BaseModel):
    product_id: int
    quantity: PositiveInt


class SReviewAdd(BaseModel):
    rate: int
    comment: str
    product_id: int


class SPage(BaseModel):
    page: PositiveInt


class SPagination(BaseModel):
    start: int
    end: int


class SReviewUser(BaseModel):
    id: int
    fullname: str


class SReviewInfo(BaseModel):
    id: int
    rate: int
    comment: str
    photo: list[SPhotos]
    user: SReviewUser
    create_at: datetime
