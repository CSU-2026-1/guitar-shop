from enum import Enum

from pydantic import BaseModel

from orders_service.app.schemas.order_items_schema import OrderItem
from orders_service.app.schemas.order_items_schema import OrderItemCreate


class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    PROCESSING = "processing"
    CANCELLED = "cancelled"


class OrderCreate(BaseModel):
    username: str | None = None
    items: list[OrderItemCreate]
    status: OrderStatus = OrderStatus.CREATED


class Order(OrderCreate):
    id: int
    username: str
    items: list[OrderItem]

    model_config = {"from_attributes": True}


class OrderUpdate(BaseModel):
    status: OrderStatus
