from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Category(BaseModel):
    __tablename__ = "category"

    name: Mapped[str]

    product: Mapped[list["Products"]] = relationship(back_populates="category", uselist=True)


class Companies(BaseModel):
    __tablename__ = "company"

    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(nullable=True)
    inn: Mapped[int] = mapped_column(unique=True, nullable=True)
    payment_details: Mapped[str] = mapped_column(nullable=True)
    legal_address: Mapped[str] = mapped_column(nullable=True)
    passport_data: Mapped[str] = mapped_column(nullable=True)
    photo: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False)

    seller: Mapped[list["Sellers"]] = relationship(back_populates="company", uselist=True)
    product: Mapped[list["Products"]] = relationship(back_populates="company", uselist=True)


class Products(BaseModel):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(85), nullable=False)
    price: Mapped[int] = mapped_column(nullable=True)
    quantity: Mapped[int] = mapped_column(nullable=True)
    rate: Mapped[int] = mapped_column(nullable=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))

    company: Mapped["Companies"] = relationship(back_populates="product")
    category: Mapped["Category"] = relationship(back_populates="product")
    order: Mapped[list["Orders"]] = relationship(back_populates="product", uselist=True)
    parameter: Mapped[list["Parameters"]] = relationship(
        back_populates="product", uselist=True
    )
    photo: Mapped[list["Photos"]] = relationship(back_populates="product", uselist=True)
    review: Mapped[list["Reviews"]] = relationship(back_populates="product", uselist=True)

    eagers = ["photo", "parameter"]


class Parameters(BaseModel):
    __tablename__ = "parameters"

    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    product: Mapped["Products"] = relationship(back_populates="parameter")


class Photos(BaseModel):
    __tablename__ = "photos"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    photo: Mapped[str]

    product: Mapped["Products"] = relationship(back_populates="photo")


class Orders(BaseModel):
    __tablename__ = "orders"

    quantity: Mapped[int]
    is_taken: Mapped[bool] = mapped_column(default=False)
    is_order: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"), nullable=True)

    user: Mapped["Users"] = relationship(back_populates="order")
    product: Mapped["Products"] = relationship(back_populates="order")
    review: Mapped["Reviews"] = relationship(back_populates="order")
    contact: Mapped["Contacts"] = relationship(back_populates="order")


class Reviews(BaseModel):
    __tablename__ = "reviews"

    rate: Mapped[int] = mapped_column()
    comment: Mapped[str]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    product: Mapped["Products"] = relationship(back_populates="review")
    user: Mapped["Users"] = relationship(back_populates="review")
    order: Mapped["Orders"] = relationship(back_populates="review")
    photo: Mapped[list["PhotoReview"]] = relationship(back_populates="review", uselist=True)

    eagers = ["photo", "user"]


class PhotoReview(BaseModel):
    __tablename__ = "photo_review"

    photo: Mapped[str]
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"))

    review: Mapped["Reviews"] = relationship(back_populates="photo")
