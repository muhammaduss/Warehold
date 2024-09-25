from fastapi import FastAPI

app = FastAPI(
    title="Warehold API Documentation",
    description="API for managaing processes on warehouse",
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
    pass


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
