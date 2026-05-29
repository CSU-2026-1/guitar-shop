from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from orders_service.app.containers.container import Container
from orders_service.app.core.security import get_current_user
from orders_service.app.schemas.orders_schemas import OrderCreate
from orders_service.app.schemas.orders_schemas import OrderUpdate
from orders_service.app.use_cases.create_order_use_case import CreateOrderUseCase
from orders_service.app.use_cases.delete_order_use_case import DeleteOrderUseCase
from orders_service.app.use_cases.get_order_use_case import GetOrderUseCase
from orders_service.app.use_cases.get_orders_use_case import GetOrdersUseCase
from orders_service.app.use_cases.update_order_use_case import UpdateOrderUseCase

router = APIRouter(prefix="/orders", tags=["Orders"])


def _order_owner(current_user: dict) -> str | None:
    if current_user.get("is_admin"):
        return None
    return current_user.get("username") or current_user.get("email")


def _username(current_user: dict) -> str:
    return current_user.get("username") or current_user.get("email")


@router.post("/", status_code=201)
@inject
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user),
    use_case: CreateOrderUseCase = Depends(Provide[Container.create_order_use_case]),
):
    try:
        order_id = await use_case.execute(order_data, _username(current_user))
        return {"order_id": order_id, "status": "created"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", status_code=200)
@inject
async def get_order(
    order_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: GetOrderUseCase = Depends(Provide[Container.get_order_use_case]),
):
    try:
        order = await use_case.execute(order_id, _order_owner(current_user))
        return {"order_data": order, "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", status_code=200)
@inject
async def get_orders(
    current_user: dict = Depends(get_current_user),
    use_case: GetOrdersUseCase = Depends(Provide[Container.get_orders_use_case]),
):
    try:
        orders = await use_case.execute(_order_owner(current_user))
        return {"orders": orders, "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{order_id}", status_code=204)
@inject
async def delete_order(
    order_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: DeleteOrderUseCase = Depends(Provide[Container.delete_order_use_case]),
):
    try:
        await use_case.execute(order_id, _order_owner(current_user))
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}", status_code=200)
@inject
async def update_order(
    order_id: int,
    update_data: OrderUpdate,
    current_user: dict = Depends(get_current_user),
    use_case: UpdateOrderUseCase = Depends(Provide[Container.update_order_use_case]),
):
    try:
        order = await use_case.execute(order_id, update_data, _order_owner(current_user))
        return {"order_data": order, "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
