from sqlalchemy import select

from app.models.user import User


class UserRepository:
    def __init__(self, session):
        self.session = session

    async def get_by_email(self, email: str):
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str):
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User):
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def rollback(self):
        await self.session.rollback()
