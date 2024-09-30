from fastapi.testclient import TestClient
from typing import AsyncGenerator
import pytest
from ..main import app, get_async_session
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
import os
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

# Создаем движок для тестовой бд

test_engine = create_async_engine(
    url=f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    + f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/test",
    echo=True,
    poolclass=NullPool,
)

test_session = async_sessionmaker(bind=test_engine, expire_on_commit=False)

# Переписываем сессию под бд 'test' (чтобы не засорять данными основную бд)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_db


client = TestClient(app)


# Выбираем asyncio как бэкенд в плагине AnyIO, нативной поддержки асинхронных
# тестов нет в Python, поэтому придется прибегнуть к такому способу


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_post_products():

    response = client.post(
        "/products",
        json={
            "title": "apples",
            "description": "some tasty apples",
            "price": 40,
            "count": 34,
        },
    )

    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_products():

    response = client.get("/products")
    assert response.status_code == 200

    data = response.json()
    assert data[0]["title"] == "apples"
    assert data[0]["description"] == "some tasty apples"
    assert data[0]["price"] == 40
    assert data[0]["count"] == 34


@pytest.mark.anyio
async def test_get_product_by_id():

    id = 1
    response = client.get(f"/products/{id}")
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "apples"
    assert data["description"] == "some tasty apples"
    assert data["price"] == 40
    assert data["count"] == 34


@pytest.mark.anyio
async def test_put_product_by_id():

    # Обновляем прайс

    id = 1
    response = client.put(
        f"/products/{id}",
        json={
            "title": "apples",
            "description": "some tasty apples",
            "price": 45,
            "count": 34,
        },
    )
    assert response.status_code == 200

    response = client.get(f"/products/{id}")
    assert response.status_code == 200

    data = response.json()
    assert data["price"] == 45


# @pytest.mark.anyio
# async def test_delete_product_by_id():
#     id = 1
#     response = client.delete(f"/products/{id}")
#     assert response.status_code == 200


@pytest.mark.anyio
async def test_post_order():

    # Проверка если у нас количество в заказе меньше чем на складе
    response = client.post("/orders", json=[{"title": "apples", "count": 27}])
    assert response.status_code == 200

    # Теперь проверим, работает ли бизнес-логика, что при заказе кол-во
    # на складе уменьшится (то есть было 34, должно остаться 7)
    id = 1
    response = client.get(f"/products/{id}")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 7

    # Проверим еще бизнес-логику: создастся ли заказ если товара не хватает
    response = client.post("/orders", json=[{"title": "apples", "count": 8}])
    assert response.status_code == 200
    assert response.json() == {"message": "Недостаточное количество товара на складе"}


@pytest.mark.anyio
async def test_get_orders():

    response = client.get("/orders")
    assert response.status_code == 200

    # created_at не проверялся, так как без взгляда на бд сложно в мс уложиться
    data = response.json()
    assert data[0]["id"] == 1
    assert data[0]["status"] == "в процессе"
    assert data[0]["products"] == [{"title": "apples", "count": 27}]


@pytest.mark.anyio
async def test_get_order_by_id():
    id = 1
    response = client.get(f"/orders/{id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert data["status"] == "в процессе"
    assert data["products"] == [{"title": "apples", "count": 27}]


@pytest.mark.anyio
async def test_patch_order_status_by_id():
    id = 1
    response = client.patch(f"/orders/{id}/status", json={"status": "отправлен"})
    assert response.status_code == 200

    # Проверка успешно ли изменен статус

    response = client.get(f"/orders/{id}")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "отправлен"
