from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Article, User
from app.models.enums import ArticleStatus, UserRole
from app.repositories.article_repository import ArticleRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.services.indexing_service import IndexingService


class ArticleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.articles = ArticleRepository(session)
        self.categories = CategoryRepository(session)
        self.indexing = IndexingService(session)

    async def list_articles(
        self,
        user: User,
        *,
        category_id: int | None = None,
        status: ArticleStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Article]:
        if user.role == UserRole.employee:
            status = ArticleStatus.published   # employees only see published (rule 8)
        return await self.articles.list(
            status=status, category_id=category_id, limit=limit, offset=offset
        )

    async def get_article(self, user: User, article_id: int) -> Article:
        """Visibility rule: a draft looks like it doesn't exist to employees (rule 10)."""
        article = await self.articles.get(article_id)
        if article is None:
            raise NotFoundError("Article not found")
        if user.role == UserRole.employee and article.status != ArticleStatus.published:
            raise NotFoundError("Article not found")
        return article

    async def create_article(self, user: User, data: ArticleCreate) -> Article:
        if await self.categories.get(data.category_id) is None:
            raise NotFoundError("Category not found")
        article = await self.articles.add(
            Article(
                title=data.title,
                body=data.body,
                category_id=data.category_id,
                author_id=user.id,      # status not set: the model default is draft (rule 9)
            )
        )
        await self.session.commit()
        return article

    async def update_article(self, article_id: int, data: ArticleUpdate) -> Article:
        article = await self._get_or_404(article_id)
        changes = {k: v for k, v in data.model_dump(exclude_unset=True).items()
                   if v is not None}
        if "category_id" in changes:
            if await self.categories.get(changes["category_id"]) is None:
                raise NotFoundError("Category not found")
        article = await self.articles.update(article, changes)
        if article.status == ArticleStatus.published and {"title", "body"} & changes.keys():
            await self.indexing.index_article(article)
        await self.session.commit()
        return article

    async def change_status(self, article_id: int, status: ArticleStatus) -> Article:
        article = await self._get_or_404(article_id)
        article = await self.articles.update(article, {"status": status})
        if status == ArticleStatus.published:
            await self.indexing.index_article(article)
        else:
            await self.indexing.remove_article(article.id)
        await self.session.commit()
        return article

    async def delete_article(self, article_id: int) -> None:
        article = await self._get_or_404(article_id)
        await self.articles.delete(article)
        await self.session.commit()

    async def _get_or_404(self, article_id: int) -> Article:
        article = await self.articles.get(article_id)
        if article is None:
            raise NotFoundError("Article not found")
        return article



