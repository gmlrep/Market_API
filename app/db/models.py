from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, func, JSON, String, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    fullname: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[str] = mapped_column(SmallInteger)
    photo: Mapped[str] = mapped_column(nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)
    hashed_password: Mapped[str]
    salt: Mapped[str]
    white_list_ip: Mapped[str]
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    is_active: Mapped[bool] = mapped_column(default=False)  # Аккаунт не удален
    is_enabled: Mapped[bool] = mapped_column(default=False)  # Аккаунт подтвердил почту
    is_baned: Mapped[bool] = mapped_column(default=False)  # Аккаунт заблокирован админом
    is_admin: Mapped[bool] = mapped_column(default=False)

    seller: Mapped['Sellers'] = relationship(back_populates='user')
    admin: Mapped['Admins'] = relationship(back_populates='user')
    order: Mapped[list['Orders']] = relationship(back_populates='user', uselist=True)
    review: Mapped[list['Reviews']] = relationship(back_populates='user', uselist=True)
    contact: Mapped['Contacts'] = relationship(back_populates='user')


class Sellers(Base):
    __tablename__ = 'sellers'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    company_role: Mapped[int] = mapped_column()
    type_company: Mapped[int] = mapped_column(SmallInteger)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped['Users'] = relationship(back_populates='seller')
    company: Mapped['Companies'] = relationship(back_populates='seller')


class Admins(Base):
    __tablename__ = 'admins'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    permission: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped['Users'] = relationship(back_populates='admin')


class Category(Base):
    __tablename__ = 'category'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    name: Mapped[str]

    product: Mapped[list['Products']] = relationship(back_populates='category', uselist=True)


class Companies(Base):
    __tablename__ = 'company'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(nullable=True)
    inn: Mapped[int] = mapped_column(unique=True, nullable=True)
    payment_details: Mapped[str] = mapped_column(nullable=True)
    legal_address: Mapped[str] = mapped_column(nullable=True)
    passport_data: Mapped[str] = mapped_column(nullable=True)
    photo: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False)

    seller: Mapped[list['Sellers']] = relationship(back_populates='company', uselist=True)
    product: Mapped[list['Products']] = relationship(back_populates='company', uselist=True)


class Orders(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    quantity: Mapped[int]  # Положительное число!
    is_taken: Mapped[bool] = mapped_column(default=False)  # False означает, что товар не получен
    is_order: Mapped[bool] = mapped_column(default=False)  # False означает, что товар в корзине
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    contact_id: Mapped[int] = mapped_column(ForeignKey('contacts.id'), nullable=True)

    user: Mapped['Users'] = relationship(back_populates='order')
    product: Mapped['Products'] = relationship(back_populates='order')
    review: Mapped['Reviews'] = relationship(back_populates='order')
    contact: Mapped['Contacts'] = relationship(back_populates='order')


class Products(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    name: Mapped[str] = mapped_column(String(85), nullable=False)
    price: Mapped[int] = mapped_column(nullable=True)  # Положительное число!
    quantity: Mapped[int] = mapped_column(nullable=True)  # Положительное число!
    rate: Mapped[int] = mapped_column(nullable=True)  # Сами заполняем + обновляем с регулярностью
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'))

    company: Mapped['Companies'] = relationship(back_populates='product')
    category: Mapped['Category'] = relationship(back_populates='product')
    order: Mapped[list['Orders']] = relationship(back_populates='product', uselist=True)
    parameter: Mapped[list['Parameters']] = relationship(back_populates='product', uselist=True)
    photo: Mapped[list['Photos']] = relationship(back_populates='product', uselist=True)
    review: Mapped[list['Reviews']] = relationship(back_populates='product', uselist=True)


class Parameters(Base):
    __tablename__ = 'parameters'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str]
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))

    product: Mapped['Products'] = relationship(back_populates='parameter')


class Photos(Base):
    __tablename__ = 'photos'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    photo: Mapped[str]

    product: Mapped['Products'] = relationship(back_populates='photo')


class Reviews(Base):
    __tablename__ = 'reviews'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    rate: Mapped[int] = mapped_column()
    comment: Mapped[str]
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    product: Mapped['Products'] = relationship(back_populates='review')
    user: Mapped['Users'] = relationship(back_populates='review')
    order: Mapped['Orders'] = relationship(back_populates='review')
    photo: Mapped[list['PhotoReview']] = relationship(back_populates='review', uselist=True)


class PhotoReview(Base):
    __tablename__ = 'photo_review'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    photo: Mapped[str]
    review_id: Mapped[int] = mapped_column(ForeignKey('reviews.id'))

    review: Mapped['Reviews'] = relationship(back_populates='photo')


class Contacts(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    city: Mapped[str]
    street: Mapped[str] = mapped_column(nullable=True)
    house: Mapped[str] = mapped_column(nullable=True)
    building: Mapped[str] = mapped_column(nullable=True)
    literal: Mapped[str] = mapped_column(nullable=True)
    apartment: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped['Users'] = relationship(back_populates='contact')
    order: Mapped[list['Orders']] = relationship(back_populates='contact', uselist=True)
