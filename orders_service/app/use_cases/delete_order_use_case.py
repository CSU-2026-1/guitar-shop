from fastapi import HTTPException

from orders_service.app.repositories.orders_repo import OrdersRepository


class DeleteOrderUseCase:
    def __init__(
        self,
        repo: OrdersRepository,
    ) -> None:
        self.repo = repo

    async def execute(self, order_id: int, username: str | None = None) -> bool:
        success = await self.repo.delete_order(order_id, username)
        if not success:
            raise HTTPException(status_code=404, detail="Order not found")
        return success
