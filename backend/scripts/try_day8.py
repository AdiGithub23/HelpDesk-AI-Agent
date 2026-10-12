import asyncio
import sys

from app.core.exceptions import AppError
from app.db.session import AsyncSessionLocal, engine
from app.services.indexing_service import IndexingService


async def main(question: str) -> None:
    async with AsyncSessionLocal() as session:
        try:
            hits = await IndexingService(session).search(question, k=4)
        except AppError as e:
            print(f"{type(e).__name__}: {e}")
            return

        if not hits:
            print("no hits")
            return

        for hit in hits:
            snippet = hit.content[:80].replace("\n", " ")
            print(f"{hit.distance:.3f} | #{hit.article_id} | {hit.title} | {snippet}")


async def run(question: str) -> None:
    try:
        await main(question)
    finally:
        await engine.dispose()


if len(sys.argv) < 2:
    raise SystemExit('Usage: python -m scripts.try_day8 "your question here"')

asyncio.run(run(sys.argv[1]))



# RUN: python -m scripts.try_day8 "How do I set up the VPN?"