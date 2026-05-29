from fastapi import HTTPException

from orders_service.app.repositories.orders_repo import OrdersRepository
from orders_service.app.schemas.order_items_schema import OrderItem
from orders_service.app.schemas.orders_schemas import Order


class GetOrderUseCase:
    def __init__(
        self,
        repo: OrdersRepository,
    ) -> None:
        self.repo = repo

    async def execute(self, order_id: int, username: str | None = None):
        order = await self.repo.get_order(order_id, username)
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        items = [OrderItem.model_validate(item) for item in order.items]

        return Order(
            username=order.username,
            status=order.status,
            items=items,
            id=order.id,
        )
