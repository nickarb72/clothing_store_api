from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.db.products import Product
from app.schemas.product import ProductCreate


class ProductService:
    """Service class for product-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_products(self) -> List[Product]:
        """
        Retrieve all products from the database.

        Returns:
            List of all Product objects
        """
        result = await self.db.execute(select(Product))
        return result.scalars().all()

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Retrieve a single product by its ID.

        Args:
            product_id: ID of the product to retrieve

        Returns:
            Product object if found, None otherwise
        """
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_products_by_category(self, category: str) -> List[Product]:
        """
        Retrieve products by category.

        Args:
            category: Category name to filter by

        Returns:
            List of Product objects in the specified category
        """
        result = await self.db.execute(
            select(Product).where(Product.category == category)
        )
        return result.scalars().all()

    async def create_product(self, product_data: ProductCreate) -> Product:
        """
        Create a new product in the database.

        Args:
            product_data: Validated product data

        Returns:
            Created Product object
        """
        db_product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            category=product_data.category,
            sizes=product_data.sizes
        )
        self.db.add(db_product)
        await self.db.flush()

        return db_product

    async def delete_product(self, product_id: int) -> bool:
        """
        Delete a product by its ID.

        Args:
            product_id: ID of the product to delete

        Returns:
            True if product was deleted, False if product not found
        """
        db_product = await self.get_product_by_id(product_id)

        if db_product:
            await self.db.delete(db_product)
            return True

        return False
