from dependency_injector import containers, providers

from app.core.config import settings
from app.core.database import Database
from app.repository import (
    UserRepository,
    SellerRepository,
    CompanyRepository,
    ProductRepository,
    CategoryRepository,
    ContactRepository,
    OrderRepository,
    ReviewRepository,
    PhotoReviewRepository,
    CustomerRepository,
)
from app.services import (
    UsersService,
    AuthService,
    SellersService,
    CustomersService,
)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.endpoints.auth",
            "app.api.v1.endpoints.customers",
            "app.api.v1.endpoints.sellers",
            "app.core.dependencies",
        ]
    )

    db = providers.Singleton(Database, db_url=settings.db_settings.db_url)

    user_repository = providers.Factory(UserRepository, session=db.provided.session)
    seller_repository = providers.Factory(SellerRepository, session=db.provided.session)
    company_repository = providers.Factory(CompanyRepository, session=db.provided.session)
    product_repository = providers.Factory(ProductRepository, session=db.provided.session)
    category_repository = providers.Factory(CategoryRepository, session=db.provided.session)
    contact_repository = providers.Factory(ContactRepository, session=db.provided.session)
    order_repository = providers.Factory(OrderRepository, session=db.provided.session)
    review_repository = providers.Factory(ReviewRepository, session=db.provided.session)
    photo_review_repository = providers.Factory(
        PhotoReviewRepository, session=db.provided.session
    )
    customer_repository = providers.Factory(CustomerRepository, session=db.provided.session)

    user_service = providers.Factory(UsersService, user_repository=user_repository)
    auth_service = providers.Factory(AuthService, user_service=user_service)
    seller_service = providers.Factory(
        SellersService,
        seller_repository=seller_repository,
        company_repository=company_repository,
        product_repository=product_repository,
        user_repository=user_repository,
    )
    customer_service = providers.Factory(
        CustomersService,
        customer_repository=customer_repository,
        product_repository=product_repository,
        category_repository=category_repository,
        contact_repository=contact_repository,
        order_repository=order_repository,
        review_repository=review_repository,
        photo_review_repository=photo_review_repository,
    )
