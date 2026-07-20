import pytest

from app.schemas.user import SUserAdd


@pytest.mark.asyncio
async def test_user_repository_create_and_find(container):
    repo = container.user_repository()
    user = await repo.create(
        {
            "fullname": "Repo User",
            "email": "repo@test.com",
            "role": 1,
            "age": 20,
            "hashed_password": "x",
            "salt": "s",
            "is_active": True,
            "is_enabled": True,
            "is_baned": False,
            "is_admin": False,
        }
    )
    assert user.id is not None
    found = await repo.find_one(filter_by={"email": "repo@test.com"})
    assert found is not None


@pytest.mark.asyncio
async def test_user_service_add_and_find(container):
    service = container.user_service()
    user_id = await service.add_one(
        SUserAdd(
            fullname="Svc User",
            email="svc@test.com",
            role=1,
            age=21,
            hashed_password="h",
            salt="s",
        )
    )
    assert user_id > 0
    found = await service.find_one(filter_by={"id": user_id})
    assert found.email == "svc@test.com"


@pytest.mark.asyncio
async def test_product_repository_get(container):
    repo = container.product_repository()
    product = await repo.get_product_info(1)
    assert product.name == "Test Product"


@pytest.mark.asyncio
async def test_product_not_found(container):
    from app.core.exceptions import NotFoundError

    repo = container.product_repository()
    with pytest.raises(NotFoundError):
        await repo.get_product_info(99999)


@pytest.mark.asyncio
async def test_category_list(container):
    service = container.customer_service()
    cats = await service.get_categories()
    assert len(cats) >= 3
