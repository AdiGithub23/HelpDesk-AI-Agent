from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Article, ArticleChunk
from app.models.enums import ArticleStatus


@dataclass
class ChunkHit:
    article_id: int
    title: str
    content: str
    distance: float


class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def delete_by_article(self, article_id: int) -> None:
        await self.session.execute(
            delete(ArticleChunk).where(ArticleChunk.article_id == article_id)
        )
        await self.session.flush()

    async def replace_for_article(
        self, article_id: int, contents: list[str], embeddings: list[list[float]]
    ) -> None:
        await self.delete_by_article(article_id)
        self.session.add_all(
            ArticleChunk(
                article_id=article_id, chunk_index=i, content=content, embedding=vector
            )
            for i, (content, vector) in enumerate(zip(contents, embeddings))
        )
        await self.session.flush()

    async def search(self, embedding: list[float], k: int = 4) -> list[ChunkHit]:
        distance = ArticleChunk.embedding.cosine_distance(embedding)
        stmt = (
            select(ArticleChunk.article_id, Article.title, ArticleChunk.content, distance)
            .join(Article, Article.id == ArticleChunk.article_id)
            .where(Article.status == ArticleStatus.published)
            .order_by(distance)
            .limit(k)
        )
        result = await self.session.execute(stmt)
        return [
            ChunkHit(article_id=r[0], title=r[1], content=r[2], distance=float(r[3]))
            for r in result.all()
        ]

