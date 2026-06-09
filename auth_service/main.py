from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.auth_router import router as auth_router

from prometheus_fastapi_instrumentator import Instrumentator
from app.database.database import engine
from app.database.database import Base
from infrastructure.consul import ConsulConfig

from app.models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Регистрация в Consul
    consul_reg = ConsulConfig(service_name="auth-service", service_port=8000)
    consul_reg.register()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    consul_reg.deregister()

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    docs_url="/api/v1/auth/docs",
    openapi_url="/api/v1/auth/openapi.json",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "auth"}


@app.get("/")
async def root():
    return {"status": "ok"}


app.include_router(auth_router)