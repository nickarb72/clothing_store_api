from fastapi import APIRouter

from app.api.endpoints import products

main_router = APIRouter()
main_router.include_router(products.router, tags=["products"])
