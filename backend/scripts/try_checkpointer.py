import asyncio
import sys

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.config import settings


async def main() -> None:
    async with AsyncPostgresSaver.from_conn_string(
        settings.checkpoint_database_url
    ) as checkpointer:
        await checkpointer.setup()
        print("checkpointer ready")


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


asyncio.run(main())




# RUN: python -m scripts.try_checkpointer