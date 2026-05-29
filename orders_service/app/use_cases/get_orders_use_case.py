from orders_service.app.repositories.orders_repo import OrdersRepository
from orders_service.app.schemas.order_items_schema import OrderItem
from orders_service.app.schemas.orders_schemas import Order


class GetOrdersUseCase:
    def __init__(self, repo: OrdersRepository) -> None:
        self.repo = repo

    async def execute(self, username: str | None = None):
        orders_orm = await self.repo.get_orders(username)

        orders_dto = []
        for order in orders_orm:
            items = [OrderItem.model_validate(item) for item in order.items]
            orders_dto.append(
                Order(
                    username=order.username,
                    status=order.status,
                    items=items,
                    id=order.id,
                )
            )

        return orders_dto
