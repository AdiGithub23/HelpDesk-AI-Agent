from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Article


class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_by_category(self, category_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Article).where(Article.category_id == category_id)
        )
        return result.scalar_one()




