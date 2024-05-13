from pydantic import BaseModel


class SCategory(BaseModel):
    category: str


class SProduct(BaseModel):
    product_id: int


class SProductsInfo(BaseModel):
    id: int
    name: str
    category_id: int
    company_id: int
    price: int | None = None
    quantity: int | None = None
    rate: int | None = None

