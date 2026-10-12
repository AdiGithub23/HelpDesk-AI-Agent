import asyncio

from app.core.exceptions import AIProviderError
from app.db.session import AsyncSessionLocal, engine
from app.models.enums import ArticleStatus
from app.repositories.article_repository import ArticleRepository
from app.services.indexing_service import IndexingService


async def main() -> None:
    async with AsyncSessionLocal() as session:
        articles = await ArticleRepository(session).list(
            status=ArticleStatus.published, limit=1000
        )
        indexing = IndexingService(session)
        for article in articles:
            try:
                await indexing.index_article(article)
                await session.commit()
                print(f"indexed  #{article.id} {article.title}")
            except AIProviderError as e:
                await session.rollback()
                print(f"FAILED   #{article.id} {article.title}: {e}")


async def run() -> None:
    try:
        await main()
    finally:
        await engine.dispose()


asyncio.run(run())

# RUN: python -m scripts.reindex_articles