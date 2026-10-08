from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Comment


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, comment_id: int) -> Comment | None:
        stmt = (
            select(Comment)
            .where(Comment.id == comment_id)
            .options(selectinload(Comment.author))
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.flush()
        return await self.get(comment.id)

    async def list_by_ticket(
        self, ticket_id: int, include_internal: bool
    ) -> list[Comment]:
        stmt = (
            select(Comment)
            .where(Comment.ticket_id == ticket_id)
            .options(selectinload(Comment.author))
        )
        if not include_internal:
            stmt = stmt.where(Comment.is_internal.is_(False))
        stmt = stmt.order_by(Comment.created_at.asc(), Comment.id.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
