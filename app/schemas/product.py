from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from decimal import Decimal


class ProductBase(BaseModel):
    """Base schema for product data."""
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, description="Product price (must be positive)")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")
    sizes: Optional[List[str]] = Field(None, description="Available sizes")

    @field_validator('price')
    def validate_price(cls, v):
        """Validate that price has no more than 2 decimal places."""
        if round(v, 2) != v:
            raise ValueError('Price must have at most 2 decimal places')
        return v


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "Product name",
                "description": "Product description",
                "price": 100.59,
                "category": "Product category",
                "sizes": ["s", "m", "xl"]
            }
        }


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    sizes: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "New product name",
                "description": "New product description",
                "price": 105.59,
                "category": "New product category",
                "sizes": ["s", "m", "xl"]
            }
        }

    @field_validator('price')
    def validate_price(cls, v):
        if v is not None and round(v, 2) != v:
            raise ValueError('Price must have at most 2 decimal places')
        return v


class ProductResponse(ProductBase):
    """Schema for product response with ID."""
    id: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 10,
                "name": "Product name",
                "description": "Product description",
                "price": 100.59,
                "category": "Product category",
                "sizes": ["s", "m", "xl"]
            }
        }


def decimal_to_float(value: Decimal) -> float:
    return float(value)


class ProductListResponse(BaseModel):
    """Schema for list of products (limited fields)."""
    id: int = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    price: Decimal = Field(..., description="Product price")
    category: str = Field(..., description="Product category")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "description": "Product information for listing (limited fields)",
            "example": {
                "id": 1,
                "name": "Classic Cotton T-Shirt",
                "price": 29.99,
                "category": "T-Shirts"
            },
        }
        json_encoders = {Decimal: decimal_to_float}
