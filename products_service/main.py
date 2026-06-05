import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.containers.gateway import Container
from app.api.product_router import router as product_router
from app.infra.db import engine
from app.infra.model import Base
from prometheus_fastapi_instrumentator import Instrumentator
from grpc_server import start_grpc_server
from app.infra.seeder import seed_guitars

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_guitars()
    grpc_task = asyncio.create_task(start_grpc_server())
    yield
    grpc_task.cancel()

def create_app() -> FastAPI:
    container = Container()
    app = FastAPI(
        title="Products Service", 
        lifespan=lifespan, 
        docs_url="/api/v1/guitars/docs",
        openapi_url="/api/v1/guitars/openapi.json"
        )
    app.container = container
    app.include_router(product_router)

    return app

app = create_app()
Instrumentator().instrument(app).expose(app)
