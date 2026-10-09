from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Article
from app.models.enums import ArticleStatus


_LOAD_RELATIONS = (
    selectinload(Article.category),
    selectinload(Article.author),
)


class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, article_id: int) -> Article | None:
        stmt = (
            select(Article)
            .where(Article.id == article_id)
            .options(*_LOAD_RELATIONS)
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        status: ArticleStatus | None = None,
        category_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Article]:
        stmt = select(Article).options(*_LOAD_RELATIONS)
        if status is not None:
            stmt = stmt.where(Article.status == status)
        if category_id is not None:
            stmt = stmt.where(Article.category_id == category_id)
        stmt = stmt.order_by(Article.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, article: Article) -> Article:
        self.session.add(article)
        await self.session.flush()
        return await self.get(article.id)

    async def update(self, article: Article, changes: dict) -> Article:
        for field, value in changes.items():
            setattr(article, field, value)
        await self.session.flush()
        return await self.get(article.id)

    async def delete(self, article: Article) -> None:
        await self.session.delete(article)
        await self.session.flush()

    async def count_by_category(self, category_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Article).where(Article.category_id == category_id)
        )
        return result.scalar_one()




