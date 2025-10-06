from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.api import main_router
from app.db.session import engine
from scripts.fill_db import init_db_with_test_data

load_dotenv()

PORT = 8000


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_with_test_data()

    yield

    await engine.dispose()


app = FastAPI(
    title="Clothing Store Catalog API",
    description="REST API for managing clothing store inventory with full CRUD operations.",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "products", "description": "Operations with products"},
    ],
)

app.include_router(main_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)
