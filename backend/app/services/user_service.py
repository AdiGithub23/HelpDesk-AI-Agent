from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.security import is_superior_agent
from app.models import User
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)

    async def get_user(self, user_id: int) -> User:
        return await self._get_or_404(user_id)

    async def list_users(self, acting_user: User, role: UserRole | None = None) -> list[User]:
        # only the superior agent sees deactivated users
        return await self.users.list(role, active_only=not is_superior_agent(acting_user))
        
    async def change_role(self, acting_user: User, user_id: int, role: UserRole) -> User:
        if acting_user.id == user_id:
            raise PermissionDeniedError("You cannot change your own role")
        user = await self._get_or_404(user_id)
        user = await self.users.update(user, {"role": role})
        await self.session.commit()
        return user

    async def set_active(self, acting_user: User, user_id: int, is_active: bool) -> User:
        if acting_user.id == user_id:
            raise PermissionDeniedError("You cannot change your own active status")
        user = await self._get_or_404(user_id)
        user = await self.users.update(user, {"is_active": is_active})
        await self.session.commit()
        return user
    
    async def _get_or_404(self, user_id: int) -> User:
        user = await self.users.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user


