from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, category_id: int) -> Category | None:
        return await self.session.get(Category, category_id)

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.session.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()

    async def list(self) -> list[Category]:
        result = await self.session.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    async def add(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.flush()
        return category

    async def update(self, category: Category, changes: dict) -> Category:
        for field, value in changes.items():
            setattr(category, field, value) # changes = {"name": "Billing"} → category.name = "Billing"
        await self.session.flush()
        return category

    async def delete(self, category: Category) -> None:
        await self.session.delete(category)
        await self.session.flush()




