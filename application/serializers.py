from pydantic import BaseModel
from datetime import datetime


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
    status: str


class GetOrderModel(BaseModel):
    id: int
    created_at: datetime
    status: str
