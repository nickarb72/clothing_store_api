import pytest
from fastapi import status

from app.db.products import Product


@pytest.mark.asyncio
async def test_get_all_products_success(client, sample_products):
    """Test successful retrieval of all products."""
    response = await client.get("/api/products/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 5

    first_product = data[0]
    assert "id" in first_product
    assert "name" in first_product
    assert "price" in first_product
    assert "category" in first_product
    assert "description" not in first_product
    assert "sizes" not in first_product


@pytest.mark.asyncio
async def test_get_products_filter_by_category(client, sample_products):
    """Test filtering products by category."""
    response = await client.get("/api/products/?category=T-Shirts")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 2
    assert all(product["category"] == "T-Shirts" for product in data)


@pytest.mark.asyncio
async def test_get_products_empty_category(client, sample_products):
    """Test filtering by non-existent category."""
    response = await client.get("/api/products/?category=NonExistent")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data == []


@pytest.mark.asyncio
async def test_get_products_case_sensitive_category(client, sample_products):
    """Test that category filter is case-sensitive."""
    response_lower = await client.get("/api/products/?category=t-shirts")
    response_upper = await client.get("/api/products/?category=T-SHIRTS")

    assert response_lower.status_code == status.HTTP_200_OK
    assert response_upper.status_code == status.HTTP_200_OK

    assert response_lower.json() == []
    assert response_upper.json() == []


@pytest.mark.asyncio
async def test_get_products_empty_database(client):
    """Test retrieving products from empty database."""
    response = await client.get("/api/products/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data == []


@pytest.mark.asyncio
async def test_get_products_response_structure(client, sample_products):
    """Test that response has correct structure and data types."""
    response = await client.get("/api/products/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    product = data[0]

    assert isinstance(product["id"], int)
    assert isinstance(product["name"], str)
    assert isinstance(product["price"], float)
    assert isinstance(product["category"], str)

    assert product["id"] > 0
    assert product["name"] != ""
    assert product["price"] > 0
    assert product["category"] != ""


@pytest.mark.asyncio
async def test_get_products_pagination_ready(client, sample_products):
    """Test that endpoint is ready for future pagination implementation."""
    response = await client.get("/api/products/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) <= 100


@pytest.mark.asyncio
async def test_get_products_with_special_characters(client, test_db_session):
    """Test products with special characters in names and categories."""
    special_product = Product(
        name="T-Shirt with 🎨 design & 100% cotton",
        description="Product with special chars",
        price=29.99,
        category="T-Shirts and Tops",
        sizes=["M", "L"]
    )
    test_db_session.add(special_product)
    await test_db_session.commit()

    response = await client.get("/api/products/?category=T-Shirts and Tops")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 1
    assert "🎨" in data[0]["name"]


@pytest.mark.asyncio
@pytest.mark.parametrize("price_value", [0, -10, 0.015])
async def test_product_validation_negative_price(client, price_value):
    """Test that products with invalid prices are rejected."""
    response = await client.post("/api/products/", json={
        "name": "Test Product",
        "description": "Test description",
        "price": price_value,
        "category": "Test Category",
        "sizes": ["M", "L"]
    })

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_products_multiple_query_params(client, sample_products):
    """Test that only category parameter is considered."""
    response = await client.get("/api/products/?category=T-Shirts&unknown_param=value")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 2
    assert all(product["category"] == "T-Shirts" for product in data)


@pytest.mark.asyncio
async def test_get_products_response_order(client, sample_products):
    """Test that products are returned in consistent order."""
    response1 = await client.get("/api/products/")
    response2 = await client.get("/api/products/")

    assert response1.status_code == status.HTTP_200_OK
    assert response2.status_code == status.HTTP_200_OK

    data1 = response1.json()
    data2 = response2.json()

    assert len(data1) == len(data2)
