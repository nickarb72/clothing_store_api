from sqlalchemy import Column, Integer, String, Text, Numeric, ARRAY
from typing import List, Optional

from app.db.session import Base


class Product(Base):
    """
    ORM model representing a product in the clothing store catalog.

    Attributes:
        id: Unique identifier for the product (primary key)
        name: Product name (e.g., "Cotton T-Shirt")
        description: Detailed product description
        price: Product price with 2 decimal precision
        category: Product category (e.g., "T-Shirts", "Jeans")
        sizes: Available sizes for the product (e.g., ["S", "M", "L"])
    """

    __tablename__ = "products"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(255), nullable=False, index=True)
    description: Optional[str] = Column(Text)
    price: float = Column(Numeric(10, 2), nullable=False)
    category: str = Column(String(100), nullable=False, index=True)
    sizes: Optional[List[str]] = Column(ARRAY(String(20)))

    def __repr__(self) -> str:
        """String representation of the Product instance."""
        return f"<Product(id={self.id}, name='{self.name}', price={self.price}, category='{self.category}')>"