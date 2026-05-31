from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db

from app.schemas.user import TokenSchema
from app.schemas.user import UserLoginSchema
from app.schemas.user import UserRegisterSchema
from app.schemas.user import UserResponseSchema

from app.repositories.user_repository import UserRepository

from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
)


@router.post("/register", response_model=UserResponseSchema)
async def register(
    data: UserRegisterSchema,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)

    service = AuthService(repository)

    return await service.register(
        email=data.email,
        username=data.username,
        password=data.password,
    )


@router.post("/login", response_model=TokenSchema)
async def login(
    data: UserLoginSchema,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)

    service = AuthService(repository)

    return await service.login(
        email=data.email,
        password=data.password,
    )
