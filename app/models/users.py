from __future__ import annotations

from sqlalchemy import ForeignKey, String, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Users(BaseModel):
    __tablename__ = "users"

    fullname: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[int] = mapped_column(SmallInteger)
    photo: Mapped[str] = mapped_column(nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)
    hashed_password: Mapped[str]
    salt: Mapped[str]
    white_list_ip: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_enabled: Mapped[bool] = mapped_column(default=False)
    is_baned: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)

    seller: Mapped["Sellers"] = relationship(back_populates="user")
    admin: Mapped["Admins"] = relationship(back_populates="user")
    order: Mapped[list["Orders"]] = relationship(back_populates="user", uselist=True)
    review: Mapped[list["Reviews"]] = relationship(back_populates="user", uselist=True)
    contact: Mapped["Contacts"] = relationship(back_populates="user")


class Sellers(BaseModel):
    __tablename__ = "sellers"

    company_role: Mapped[int] = mapped_column()
    type_company: Mapped[int] = mapped_column(SmallInteger)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["Users"] = relationship(back_populates="seller")
    company: Mapped["Companies"] = relationship(back_populates="seller")


class Admins(BaseModel):
    __tablename__ = "admins"

    permission: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["Users"] = relationship(back_populates="admin")


class Contacts(BaseModel):
    __tablename__ = "contacts"

    city: Mapped[str]
    street: Mapped[str] = mapped_column(nullable=True)
    house: Mapped[str] = mapped_column(nullable=True)
    building: Mapped[str] = mapped_column(nullable=True)
    literal: Mapped[str] = mapped_column(nullable=True)
    apartment: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["Users"] = relationship(back_populates="contact")
    order: Mapped[list["Orders"]] = relationship(back_populates="contact", uselist=True)
