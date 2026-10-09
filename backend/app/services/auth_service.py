from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)

    async def register(self, data: RegisterRequest) -> User:
        email = data.email.lower()
        if await self.users.get_by_email(email):
            raise ConflictError("Email already registered")
        user = await self.users.add(
            User(
                email=email,
                full_name=data.full_name,
                hashed_password=hash_password(data.password),
                role=UserRole.employee,
            )
        )
        await self.session.commit()
        return user

    async def login(self, email: str, password: str) -> str:
        user = await self.users.get_by_email(email.lower())
        if (
            user is None
            or not verify_password(password, user.hashed_password)
            or not user.is_active
        ):
            raise AuthenticationError("Incorrect email or password")
        return create_access_token(user.id)

    async def get_user_from_token(self, token: str) -> User:
        user_id = decode_access_token(token)
        user = await self.users.get(user_id) if user_id is not None else None
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid or expired token")
        return user



