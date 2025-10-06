import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine, Base, AsyncSessionLocal


async def fill_test_db(session: AsyncSession):
    """Fill database with test data for development and testing."""
    pass

    print("✅ Test database filled successfully!")


async def create_test_data(session: AsyncSession):
    try:
        await fill_test_db(session)
    except Exception as exc:
        print(f"\n❌ Exception has occurred while test data was creating: {exc}")
        raise


async def init_db_with_test_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            await create_test_data(session)


if __name__ == "__main__":
    asyncio.run(init_db_with_test_data())
