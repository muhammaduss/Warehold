from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, delete
from models import Product, Order, OrderItem
from serializers import (
    CreateProductModel, GetProductModel, CreateOrderModel,
    GetOrderModel, UpdateOrderModelStatus
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
            last_id = 0
        else:
            last_id = last.id

        product = Product(
            id=last_id + 1,
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
async def post_order(data: List[CreateOrderModel]):
    async with session() as s:

        '''

        Важные спецификации:

        - Запрос скорее всего подразумевается что будет лист товаров.

        - В ТЗ не указано, мы получаем индекс товара или его имя в теле POST
        запроса, так что для удобства юзеров - решил что лучше сделать
        поля "название товара" и "количество". А айди товара для OrderItem
        получаем потом по квери в таблице Products.

        - Статус заказа после создания заказа будет "в процессе", с последующей
        возможностью сменить в ендпоинте PATCH /orders/{id}/status

        '''

        # Получаем id из таблицы Order

        statement = select(Order).order_by(Order.id.desc())
        result = await s.execute(statement)

        orders_last = result.scalars().first()
        if orders_last is None:
            orders_last_id = 1
        else:
            orders_last_id = orders_last.id + 1

        order = Order(
            id=orders_last_id,
            created_at=datetime.now(),
            status="в процессе"
        )

        s.add(order)
        await s.commit()

        for entry in data:

            # Получаем id из таблиц Products и OrderItem

            statement = select(Product).filter(
                Product.title == entry.title).order_by(Product.id.desc())
            result = await s.execute(statement)

            products_last = result.scalars().first()
            if products_last is None:
                return {"message": f"Товара '{entry.title}' нет на складе"}

            statement = select(OrderItem).order_by(OrderItem.id.desc())
            result = await s.execute(statement)

            order_items_last = result.scalars().first()
            if order_items_last is None:
                order_items_last_id = 0
            else:
                order_items_last_id = order_items_last.id

            # Запись в таблицу OrderItem

            order_item = OrderItem(
                id=order_items_last_id + 1,
                product_id=products_last.id,
                order_id=orders_last_id,
                count=entry.count
            )

            s.add(order_item)
            await s.commit()


@app.get("/orders", response_model=List[GetOrderModel])
async def get_orders():
    async with session() as s:

        statement = select(Order).order_by(Order.id)
        result = await s.execute(statement)
        orders = result.scalars()

        response = []

        if orders is None:
            return response

        for order in orders:
            response.append(await get_order_by_id(order.id))

        return response


@app.get("/orders/{id}", response_model=GetOrderModel)
async def get_order_by_id(id):
    async with session() as s:

        statement = select(Order).filter(Order.id == int(id))
        result = await s.execute(statement)
        order = result.scalars().one()

        if order is None:
            return {"message": f"Заказа с id {id} не существует"}

        response = {
            "id": order.id,
            "created_at": order.created_at,
            "status": order.status,
            "products": []
        }

        # Фильтруем продукты с OrderItem и Product которые
        # соответствуют заказу с данным id

        statement = select(OrderItem).filter(OrderItem.order_id == order.id)
        result = await s.execute(statement)
        order_products = result.scalars()

        for order_product in order_products:

            statement = select(Product).filter(
                Product.id == order_product.product_id)
            result = await s.execute(statement)
            product = result.scalars().one()

            response["products"].append(
                {"title": product.title, "count": order_product.count})

        return response


@app.patch("/orders/{id}/status")
async def update_order_status_by_id(id, data: UpdateOrderModelStatus):
    async with session() as s:

        statement = select(Order).filter(Order.id == int(id))
        result = await s.execute(statement)

        order = result.scalars().one()
        order.status = data.status

        await s.commit()
