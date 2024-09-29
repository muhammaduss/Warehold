from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from models import Product
from db import engine

app = FastAPI(
    title="Warehold API Documentation",
    description="API for managaing processes on warehouse",
)

session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


@app.get("/")
def root():
    return {"Hello": "World"}


# Эндпоинты для товаров
@app.post("/products")
async def post_product():
    pass


@app.get("/products")
async def get_products():
    async with session() as s:
        statement = select(Product).order_by(Product.id)
        result = await s.execute(statement)
        return result.scalars().first()
#


@app.get("/products/{id}")
async def get_product_by_id(id):
    pass


@app.put("/products/{id}")
async def put_product_by_id(id):
    pass


@app.delete("/products/{id}")
async def delete_product_by_id(id):
    pass


# Эндпоинты для заказов

@app.post("/orders")
async def post_order():
    pass


@app.get("/orders")
async def get_orders():
    pass


@app.get("/orders/{id}")
async def get_order_by_id(id):
    pass


@app.patch("/orders/{id}/status")
async def get_order_status_by_id(id):
    pass


# @app.get("/items/{item_id}")
# async def read_item(item_id):
#     return {"item_id": item_id}
