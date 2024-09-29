from db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, ForeignKey
from datetime import datetime


class Product(Base):
    __tablename__ = 'Product'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int]
    count: Mapped[int]


class Order(Base):
    __tablename__ = 'Order'
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now, nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)


class OrderItem(Base):
    __tablename__ = 'OrderItem'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("Product.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("Order.id"))
    count: Mapped[int]
