from dependency_injector import providers, containers
from broker.kafka.client.kafka_client import KafkaClient
from orders_service.app.repositories.orders_repo import OrdersRepository
from orders_service.app.use_cases.delete_order_use_case import DeleteOrderUseCase
from orders_service.app.use_cases.create_order_use_case import CreateOrderUseCase
from orders_service.app.use_cases.get_order_use_case import GetOrderUseCase
from orders_service.app.use_cases.get_orders_use_case import GetOrdersUseCase
from orders_service.app.use_cases.update_order_use_case import UpdateOrderUseCase
from orders_service.config import settings
from orders_service.infra.database.db_config import Database
from orders_service.infra.kafka.producers.order_created_producer import OrderCreatedProducer

class Container(containers.DeclarativeContainer):

    config = providers.Object(settings)

    db_write = providers.Singleton(
        Database,
        db_url = config.provided.db_url
    )

    db_read = providers.Singleton(
        Database,
        db_url = config.provided.db_replica_url
    )

    orders_repo_write = providers.Factory(
        OrdersRepository,
        session_factory=db_write.provided.get_session_factory.call(),
    )

    orders_repo_read = providers.Factory(
        OrdersRepository,
        session_factory=db_read.provided.get_session_factory.call(),
    )

    kafka_client = providers.Singleton(
        KafkaClient,
        config.provided.bootstrap_servers,
    )

    order_created_producer = providers.Factory(
        OrderCreatedProducer,
        kafka_client,
    )


    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        repo=orders_repo_write,
        producer=order_created_producer,
    )

    get_order_use_case = providers.Factory(
        GetOrderUseCase,
        repo=orders_repo_read,
    )

    get_orders_use_case = providers.Factory(
        GetOrdersUseCase,
        repo=orders_repo_read,
    )

    delete_order_use_case = providers.Factory(
        DeleteOrderUseCase,
        repo=orders_repo_write,
    )

    update_order_use_case = providers.Factory(
        UpdateOrderUseCase,
        repo=orders_repo_write,
    )