from datetime import datetime

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
    price: PositiveInt | None = None
    quantity: PositiveInt | None = None
    rate: int | None = None


class SContact(BaseModel):
    city: str | None = None
    street: str | None = None
    house: str | None = None
    building: str | None = None
    literal: str | None = None
    apartment: str | None = None


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
    contact: SContact | None
    order: list[SOrderInfo]
    photo: str | None
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
