import asyncio

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, engine
from app.models import User
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository


async def main() -> None:
    if not settings.seed_agent_email or not settings.seed_agent_password:
        raise SystemExit(
            "SEED_AGENT_EMAIL and SEED_AGENT_PASSWORD must be set in .env"
        )

    email = settings.seed_agent_email.lower()

    async with AsyncSessionLocal() as session:
        users = UserRepository(session)

        if await users.get_by_email(email):
            print(f"Agent {email} already exists")
            return

        await users.add(
            User(
                email=email,
                full_name="Seed Agent",
                hashed_password=hash_password(settings.seed_agent_password),
                role=UserRole.agent,
            )
        )
        await session.commit()
        print(f"Agent {email} created")


async def run() -> None:
    try:
        await main()
    finally:
        await engine.dispose()


asyncio.run(run())