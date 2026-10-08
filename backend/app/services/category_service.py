from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models import Category
from app.repositories.article_repository import ArticleRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.categories = CategoryRepository(session)
        self.tickets = TicketRepository(session)
        self.articles = ArticleRepository(session)

    async def list_categories(self) -> list[Category]:
        return await self.categories.list()

    async def create_category(self, data: CategoryCreate) -> Category:
        if await self.categories.get_by_name(data.name):
            raise ConflictError("A category with this name already exists")
        category = await self.categories.add(
            Category(name=data.name, description=data.description)
        )
        await self.session.commit()
        return category

    async def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        category = await self._get_or_404(category_id)
        changes = {k: v for k, v in data.model_dump(exclude_unset=True).items()
                   if not (k == "name" and v is None)}
        new_name = changes.get("name")
        if new_name and new_name != category.name:
            if await self.categories.get_by_name(new_name):
                raise ConflictError("A category with this name already exists")
        category = await self.categories.update(category, changes)
        await self.session.commit()
        return category

    async def delete_category(self, category_id: int) -> None:
        category = await self._get_or_404(category_id)
        in_use = await self.tickets.count_by_category(category_id)
        in_use += await self.articles.count_by_category(category_id)
        if in_use:
            raise ConflictError("Category still has tickets or articles")
        await self.categories.delete(category)
        await self.session.commit()

    async def _get_or_404(self, category_id: int) -> Category:
        category = await self.categories.get(category_id)
        if category is None:
            raise NotFoundError("Category not found")
        return category




