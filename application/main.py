from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, delete
from models import Product, Order
from serializers import (
    CreateProductModel, GetProductModel, CreateOrderModel, GetOrderModel
)
from typing import List
from db import engine
from datetime import datetime

app = FastAPI(
    title="Warehold API Documentation",
    description="API for managaing processes on warehouse",
)

# Создание сессии в БД

session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


# Эндпоинты для товаров

@app.post("/products")
async def post_product(data: CreateProductModel):
    async with session() as s:

        statement = select(Product).order_by(Product.id.desc())
        result = await s.execute(statement)

        last = result.scalars().first()
        if last is None:
            last.id = 0

        product = Product(
            id=last.id + 1,
            title=data.title,
            description=data.description,
            price=data.price,
            count=data.count
        )

        s.add(product)
        await s.commit()


@app.get("/products", response_model=List[GetProductModel])
async def get_products():
    async with session() as s:

        statement = select(Product).order_by(Product.id)
        result = await s.execute(statement)

        return result.scalars()


@app.get("/products/{id}")
async def get_product_by_id(id):
    async with session() as s:

        statement = select(Product).filter(Product.id == int(id))
        result = await s.execute(statement)

        return result.scalars().one()


@app.put("/products/{id}")
async def put_product_by_id(id, data: GetProductModel):
    async with session() as s:

        statement = select(Product).filter(Product.id == int(id))
        result = await s.execute(statement)

        product = result.scalars().one()
        product.title = data.title
        product.description = data.description
        product.price = data.price
        product.count = data.count

        await s.commit()


@app.delete("/products/{id}")
async def delete_product_by_id(id):
    async with session() as s:

        statement = delete(Product).filter(Product.id == int(id))

        await s.execute(statement)
        await s.commit()


# Эндпоинты для заказов

@app.post("/orders")
async def post_order(data: CreateOrderModel):
    async with session() as s:

        statement = select(Order).order_by(Order.id.desc())
        result = await s.execute(statement)

        last = result.scalars().first()
        if last is None:
            last.id = 0

        order = Order(
            id=last.id + 1,
            datetime=datetime.now().isoformat(),
            status=data.status
        )

        s.add(order)
        await s.commit()


@app.get("/orders", response_model=List[GetOrderModel])
async def get_orders():
    async with session() as s:

        statement = select(Order).order_by(Order.id)
        result = await s.execute(statement)

        return result.scalars()


@app.get("/orders/{id}")
async def get_order_by_id(id):
    async with session() as s:

        statement = select(Order).filter(Order.id == int(id))
        result = await s.execute(statement)

        return result.scalars().one()


@app.patch("/orders/{id}/status")
async def get_order_status_by_id(id, data: GetOrderModel):
    async with session() as s:

        statement = select(Order).filter(Order.id == int(id))
        result = await s.execute(statement)

        order = result.scalars().one()
        order.status = data.status

        await s.commit()
