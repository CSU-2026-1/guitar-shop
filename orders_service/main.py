import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from orders_service.app.containers.container import Container
from orders_service.app.api.orders_routes import router as orders_router
from orders_service.infra.database.db_config import Base
from prometheus_fastapi_instrumentator import Instrumentator

container = Container()
container.wire(modules=["orders_service.app.api.orders_routes"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_master = container.db_write()
    async with db_master._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    kafka_client = container.kafka_client()
    await kafka_client.start()

    yield

    await kafka_client.stop()

app = FastAPI(
    title="Orders Service", 
    lifespan=lifespan ,
    docs_url="/api/v1/orders/docs",
    openapi_url="/api/v1/orders/openapi.json"
    )

Instrumentator().instrument(app).expose(app)

app.include_router(orders_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("orders_service.main:app", host="0.0.0.0", port=8002, reload=True)