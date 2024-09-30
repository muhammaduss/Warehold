from pydantic import BaseModel
from datetime import datetime
from typing import List


class CreateProductModel(BaseModel):
    title: str
    description: str
    price: int
    count: int


class GetProductModel(BaseModel):
    id: int
    title: str
    description: str
    price: int
    count: int


class CreateOrderModel(BaseModel):
    title: str
    count: int


class GetOrderModel(BaseModel):
    id: int
    created_at: datetime
    status: str
    products: List[CreateOrderModel]


class UpdateOrderModelStatus(BaseModel):
    status: str
