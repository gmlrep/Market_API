from sqladmin import ModelView
from sqladmin._menu import CategoryMenu, ViewMenu
from starlette.requests import Request

from app.db.models import Users, Category, Companies, Orders, Products, Reviews


class UserModelView(ModelView, model=Users):
    name = 'User'
    column_list = [
        Users.id,
        Users.fullname,
        Users.email,
        Users.role,
    ]


class CategoryModelView(ModelView, model=Category):
    name = 'Category'
    column_list = [
        Category.id,
        Category.name
    ]


class CompanyModelView(ModelView, model=Companies):
    name = 'Company'
    column_list = [
        Companies.id,
        Companies.name,
        Companies.is_active
    ]


class OrderModelView(ModelView, model=Orders):
    name = 'Order'
    column_list = [
        Orders.id,
        Orders.user_id,
        Orders.is_order,
        Orders.is_taken
    ]


class ProductModelView(ModelView, model=Products):
    name = 'Product'
    column_list = [
        Products.id,
        Products.name,
        Products.company_id,
        Products.quantity
    ]


class ReviewModelView(ModelView, model=Reviews):
    name = 'Review'
    column_list = [
        Reviews.id,
        Reviews.user_id,
        Reviews.product_id,
        Reviews.rate
    ]
