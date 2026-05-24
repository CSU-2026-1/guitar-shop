from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.auth_router import router as auth_router

from prometheus_fastapi_instrumentator import Instrumentator
from app.database.database import engine
from app.database.database import Base

from app.models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    docs_url="/auth/docs",
    openapi_url="/auth/openapi.json",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)


@app.get("/")
async def root():
    return {"status": "ok"}


app.include_router(auth_router)