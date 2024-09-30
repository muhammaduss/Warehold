from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, delete
from models import Product, Order, OrderItem
from serializers import (
    CreateProductModel,
    GetProductModel,
    CreateOrderModel,
    GetOrderModel,
    UpdateOrderModelStatus,
)
from typing import List, AsyncGenerator
from db import engine
from datetime import datetime

app = FastAPI(
    title="Warehold API Documentation",
    description="API for managaing processes on warehouse",
)

# Создание сессии в БД

session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with session() as db_session:
        yield db_session


# Эндпоинты для товаров


@app.post("/products")
async def post_product(
    data: CreateProductModel, session: AsyncSession = Depends(get_async_session)
):

    statement = select(Product).order_by(Product.id.desc())
    result = await session.execute(statement)

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
        count=data.count,
    )

    session.add(product)
    await session.commit()


@app.get("/products", response_model=List[GetProductModel])
async def get_products(session: AsyncSession = Depends(get_async_session)):

    statement = select(Product).order_by(Product.id)
    result = await session.execute(statement)

    return result.scalars()


@app.get("/products/{id}")
async def get_product_by_id(id, session: AsyncSession = Depends(get_async_session)):

    statement = select(Product).filter(Product.id == int(id))
    result = await session.execute(statement)

    return result.scalars().one()


@app.put("/products/{id}")
async def put_product_by_id(
    id, data: GetProductModel, session: AsyncSession = Depends(get_async_session)
):

    statement = select(Product).filter(Product.id == int(id))
    result = await session.execute(statement)

    product = result.scalars().one()
    product.title = data.title
    product.description = data.description
    product.price = data.price
    product.count = data.count

    await session.commit()


@app.delete("/products/{id}")
async def delete_product_by_id(id, session: AsyncSession = Depends(get_async_session)):

    statement = delete(Product).filter(Product.id == int(id))

    await session.execute(statement)
    await session.commit()


# Эндпоинты для заказов


@app.post("/orders")
async def post_order(
    data: List[CreateOrderModel], session: AsyncSession = Depends(get_async_session)
):
    """

    Важные спецификации:

    - Запрос скорее всего подразумевается что будет лист товаров.

    - В ТЗ не указано, мы получаем индекс товара или его имя в теле POST
    запроса, так что для удобства юзеров - решил что лучше сделать
    поля "название товара" и "количество". А айди товара для OrderItem
    получаем потом по квери в таблице Products.

    - Статус заказа после создания заказа будет "в процессе", с последующей
    возможностью сменить в ендпоинте PATCH /orders/{id}/status

    """

    # Получаем id из таблицы Order

    statement = select(Order).order_by(Order.id.desc())
    result = await session.execute(statement)

    orders_last = result.scalars().first()
    if orders_last is None:
        orders_last_id = 1
    else:
        orders_last_id = orders_last.id + 1

    order = Order(id=orders_last_id, created_at=datetime.now(), status="в процессе")

    session.add(order)
    await session.commit()

    for entry in data:

        # Получаем id из таблиц Products и OrderItem

        statement = select(Product).filter(Product.title == entry.title)
        result = await session.execute(statement)

        product = result.scalars().first()
        if product is None:
            statement = delete(Order).filter(Order.id == orders_last_id)

            await session.execute(statement)
            await session.commit()

            return {"message": f"Товара '{entry.title}' нет на складе"}

        # Проверка достаточного количества товара на складе для заказа
        if product.count < entry.count:
            statement = delete(Order).filter(Order.id == orders_last_id)

            await session.execute(statement)
            await session.commit()

            return {"message": "Недостаточное количество товара на складе"}

        statement = select(OrderItem).order_by(OrderItem.id.desc())
        result = await session.execute(statement)

        order_items_last = result.scalars().first()
        if order_items_last is None:
            order_items_last_id = 0
        else:
            order_items_last_id = order_items_last.id

        # Запись в таблицу OrderItem

        order_item = OrderItem(
            id=order_items_last_id + 1,
            product_id=product.id,
            order_id=orders_last_id,
            count=entry.count,
        )

        # Обновление количества товара на складе при создании заказа
        product.count -= entry.count

        session.add(order_item)
        await session.commit()


@app.get("/orders", response_model=List[GetOrderModel])
async def get_orders(session: AsyncSession = Depends(get_async_session)):

    statement = select(Order).order_by(Order.id)
    result = await session.execute(statement)
    orders = result.scalars()

    response = []

    if orders is None:
        return response

    for order in orders:
        response.append(await get_order_by_id(order.id, session))

    return response


@app.get("/orders/{id}", response_model=GetOrderModel)
async def get_order_by_id(id, session: AsyncSession = Depends(get_async_session)):

    statement = select(Order).filter(Order.id == int(id))
    result = await session.execute(statement)
    order = result.scalars().first()

    if order is None:
        return {"message": f"Заказа с id {id} не существует"}

    response = {
        "id": order.id,
        "created_at": order.created_at,
        "status": order.status,
        "products": [],
    }

    # Фильтруем продукты с OrderItem и Product которые
    # соответствуют заказу с данным id

    statement = select(OrderItem).filter(OrderItem.order_id == order.id)
    result = await session.execute(statement)
    order_products = result.scalars()

    for order_product in order_products:

        statement = select(Product).filter(Product.id == order_product.product_id)
        result = await session.execute(statement)
        product = result.scalars().first()

        response["products"].append(
            {"title": product.title, "count": order_product.count}
        )

    return response


@app.patch("/orders/{id}/status")
async def update_order_status_by_id(
    id, data: UpdateOrderModelStatus, session: AsyncSession = Depends(get_async_session)
):

    statement = select(Order).filter(Order.id == int(id))
    result = await session.execute(statement)

    order = result.scalars().first()
    order.status = data.status

    await session.commit()
