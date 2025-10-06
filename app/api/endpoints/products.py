from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductListResponse
from app.services.product import ProductService

router = APIRouter(prefix="/products")


@router.get(
    "/",
    response_model=List[ProductListResponse],
    summary="Get products list",
    description="Retrieve a paginated list of products with optional category filtering",
)
async def get_products_list(
        category: Optional[str] = Query(None, description="Filter products by category"),
        db: AsyncSession = Depends(get_db)
) -> List[ProductListResponse]:
    """
    Retrieve a list of products.
    """
    service = ProductService(db)

    try:
        if category:
            products = await service.get_products_by_category(category)
        else:
            products = await service.get_all_products()

        return [ProductListResponse.model_validate(product) for product in products]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting products: {str(e)}"
        )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Retrieve detailed information about a specific product by its unique ID",
    responses={404: {"description": "Category not found"}},
    response_model_exclude_none=True,
)
async def get_product(
        product_id: int,
        db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Retrieve detailed information about a specific product.
    """
    service = ProductService(db)
    try:
        product = await service.get_product_by_id(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )

        return product
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting product: {str(e)}"
        )


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new product",
    description="Create a new product in the catalog. All fields except description and sizes are required",
)
async def create_product(
        product_data: ProductCreate,
        db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Create a new product.
    """
    service = ProductService(db)

    try:
        return await service.create_product(product_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating product: {str(e)}"
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product by ID",
    description="Permanently delete a product from the catalog by its ID",
    responses={404: {"description": "Product not found"}},
)
async def delete_product(
        product_id: int,
        db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a product by ID.
    """
    service = ProductService(db)

    try:
        success = await service.delete_product(product_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting product: {str(e)}"
        )
