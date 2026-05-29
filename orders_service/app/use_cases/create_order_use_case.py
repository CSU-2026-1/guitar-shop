import grpc
from fastapi import HTTPException

from event_contracts.orders.order_created_event import OrderCreatedEvent
from orders_service.app.repositories.orders_repo import OrdersRepository
from orders_service.app.schemas.orders_schemas import OrderCreate
from orders_service.infra.kafka.producers.order_created_producer import OrderCreatedProducer
from protobufs import product_pb2
from protobufs import product_pb2_grpc


class CreateOrderUseCase:
    def __init__(
        self,
        repo: OrdersRepository,
        producer: OrderCreatedProducer,
    ) -> None:
        self.repo = repo
        self.producer = producer

    async def execute(self, order: OrderCreate, username: str):
        order = order.model_copy(update={"username": username})

        async with grpc.aio.insecure_channel("products_service:50051") as channel:
            stub = product_pb2_grpc.ProductServiceStub(channel)

            for item in order.items:
                try:
                    response = await stub.GetProduct(
                        product_pb2.GetProductRequest(product_id=item.product_id)
                    )

                    if not response.exists:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Гитара с ID {item.product_id} не существует в каталоге товаров.",
                        )

                    item.title = response.title
                    item.sku = response.sku
                    item.brand = response.brand
                    item.price = response.price
                    item.type = response.type
                    item.body_wood = response.body_wood
                    item.neck_wood = response.neck_wood
                    item.fretboard_wood = response.fretboard_wood
                    item.fret_count = response.fret_count
                    item.scale_length = response.scale_length
                    item.pickup_config = response.pickup_config
                    item.image_url = response.image_url if response.image_url else None

                except grpc.RpcError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Ошибка gRPC при связи с сервисом продуктов: {e.details()}",
                    )

        order_id: int = await self.repo.create_order(order)

        event = OrderCreatedEvent(
            username=order.username,
            order_id=order_id,
        )

        await self.producer.publish(event)

        return order_id
