from fastapi import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError

from app.core.jwt import create_access_token
from app.core.security import hash_password
from app.core.security import verify_password
from app.models.user import User


class AuthService:
    def __init__(self, repository):
        self.repository = repository

    async def register(
        self,
        email: str,
        username: str,
        password: str,
    ):
        existing_email = await self.repository.get_by_email(email)

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        existing_username = await self.repository.get_by_username(username)

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
        )

        try:
            return await self.repository.create(user)
        except IntegrityError:
            await self.repository.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

    async def login(
        self,
        email: str,
        password: str,
    ):
        user = await self.repository.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "username": user.username,
                "is_admin": user.is_admin,
                "role": "admin" if user.is_admin else "user",
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
