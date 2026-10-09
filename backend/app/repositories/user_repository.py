from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.enums import UserRole


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list(self, role: UserRole | None = None) -> list[User]:
        stmt = select(User).order_by(User.id)
        if role is not None:
            stmt = stmt.where(User.role == role)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)   # loads created_at, which the DB generated
        return user

    async def update(self, user: User, changes: dict) -> User:
        for field, value in changes.items():
            setattr(user, field, value)
        await self.session.flush()
        return user



