from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, func, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    fullname: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[str] = mapped_column(default='users')
    # photo: Mapped[str] = mapped_column()
    age: Mapped[int]
    hashed_password: Mapped[str]
    salt: Mapped[str]
    white_list_ip: Mapped[str]
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    is_active: Mapped[bool] = mapped_column(default=False)
    is_enabled: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)

#Тут я забыл нужно ли использовать uselist или нет, поэтому будет время посмотри, но вроде как не нужно
    seller: Mapped['Sellers'] = relationship(back_populates='user', uselist=True)
    admin: Mapped['Admins'] = relationship(back_populates='user', uselist=True)
    token: Mapped['Tokens'] = relationship(back_populates='user', uselist=True)
    order: Mapped['Orders'] = relationship(back_populates='user')
    review: Mapped['Users'] = relationship(back_populates='user')


class Sellers(Base):
    __tablename__ = 'sellers'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    # Тут я бы добавил всё такие строку, удобней писать владелец или менеджер даже в админ панели чем 1, 2, также в типе
    company_role: Mapped[int] = mapped_column()
    type_company: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped['Users'] = relationship(back_populates='seller')
    company: Mapped['CompanyInfo'] = relationship(back_populates='seller')


class Admins(Base):
    __tablename__ = 'admins'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    permisson: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped['Users'] = relationship(back_populates='admin')


class Tokens(Base):
    __tablename__ = 'tokens'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['Users'] = relationship(back_populates='token')


class Category(Base):
    __tablename__ = 'category'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    name: Mapped[str]

    product: Mapped['Products'] = relationship(back_populates='category')


class CompanyInfo(Base):
    __tablename__ = 'company'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    name: Mapped[str] = mapped_column(String(60), unique=True)
    description: Mapped[str]
    INN: Mapped[str] = mapped_column(String(12), unique=True)
    payment_details: Mapped[str] = ... #Не знаю что это такое
    legal_address: Mapped[str]
    passport_data: Mapped[str] = mapped_column(String(11), unique=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    # photo: Mapped[str] = mapped_column()
    seller_id: Mapped[int] = mapped_column(ForeignKey('sellers.id'))

    seller: Mapped['Sellers'] = relationship(back_populates='company')
    product: Mapped['Products'] = relationship(back_populates='company')


class Orders(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    quantity: Mapped[int] #Положительное число!
    is_taken: Mapped[bool] = mapped_column(default=False) #False означает, что товар не получен
    is_order: Mapped[bool] = mapped_column(default=False) #False означает, что товар в корзине
    company_id: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))

    user: Mapped['Users'] = relationship(back_populates='order')
    product: Mapped['Products'] = relationship(back_populates='order')
    review: Mapped['Orders'] = relationship(back_populates='order')


class Products(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    name: Mapped[str] = mapped_column(String(85), nullable=False)
    price: Mapped[int] = mapped_column() #Положительное число!
    quantity: Mapped[int] = mapped_column() #Положительное число!
    rate: Mapped[int] = mapped_column() #Сами заполняем + обновляем с регулярностью
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'))

    company: Mapped['CompanyInfo'] = relationship(back_populates='product')
    category: Mapped['Category'] = relationship(back_populates='product')
    order: Mapped['Orders'] = relationship(back_populates='product')
    parameter: Mapped['Parameters'] = relationship(back_populates='product')
    photo: Mapped['Products'] = relationship(back_populates='product')
    review: Mapped['Reviews'] = relationship(back_populates='product')


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

    # photo

    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped['Products'] = relationship(back_populates='photo')


class Reviews(Base):
    __tablename__ = 'reviews'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    rate: Mapped[int] = mapped_column() #Сами заполняем + обновляем с регулярностью
    comment: Mapped[str]
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    product: Mapped['Products'] = relationship(back_populates='review')
    user: Mapped['Users'] = relationship(back_populates='review')
    order: Mapped['Orders'] = relationship(back_populates='review')
    photo: Mapped['PhotoReview'] = relationship(back_populates='review')


class PhotoReview(Base):
    __tablename__ = 'photo_review'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    # photo
    review_id: Mapped[int] = mapped_column(ForeignKey('reviews.id'))

    review: Mapped['Reviews'] = relationship(back_populates='photo')


class Contacts(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    city = ...
    street = ...
    house = ...
    corpus = ...
    literal = ...
    apartement = ...

    #TODO: add supports