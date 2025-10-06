import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

from app.core.config import DATABASE_URL
from app.main import app
from app.db.session import get_db, Base
from app.db.products import Product

TEST_DATABASE_URL = DATABASE_URL


@pytest_asyncio.fixture(scope="function")
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    AsyncTestingSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncTestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db_session: AsyncSession):
    """Create test client with overridden database dependency."""

    async def override_get_db():
        yield test_db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        app.dependency_overrides[get_db] = override_get_db
        yield test_client
        app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def sample_products(test_db_session: AsyncSession):
    """Create sample products for testing."""
    products = [
        Product(
            name="Cotton T-Shirt",
            description="Comfortable cotton t-shirt",
            price=25.99,
            category="T-Shirts",
            sizes=["S", "M", "L"]
        ),
        Product(
            name="Slim Fit Jeans",
            description="Modern slim fit jeans",
            price=89.99,
            category="Pants",
            sizes=["30", "32", "34"]
        ),
        Product(
            name="Winter Jacket",
            description="Warm winter jacket",
            price=149.99,
            category="Outerwear",
            sizes=["M", "L", "XL"]
        ),
        Product(
            name="Summer Dress",
            description="Light summer dress",
            price=59.99,
            category="Dresses",
            sizes=["S", "M", "L"]
        ),
        Product(
            name="Sports T-Shirt",
            description="Breathable sports t-shirt",
            price=35.99,
            category="T-Shirts",
            sizes=["M", "L", "XL"]
        )
    ]

    test_db_session.add_all(products)
    await test_db_session.commit()

    for product in products:
        await test_db_session.refresh(product)

    return products
