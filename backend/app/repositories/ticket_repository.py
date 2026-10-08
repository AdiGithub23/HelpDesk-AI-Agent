from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Ticket
from app.models.enums import TicketStatus

_LOAD_RELATIONS = (
    selectinload(Ticket.category),
    selectinload(Ticket.creator),
    selectinload(Ticket.assignee),
)


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, ticket_id: int) -> Ticket | None:
        stmt = (
            select(Ticket)
            .where(Ticket.id == ticket_id)
            .options(*_LOAD_RELATIONS)
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        created_by: int | None = None,
        status: TicketStatus | None = None,
        category_id: int | None = None,
        assigned_to: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Ticket]:
        stmt = select(Ticket).options(*_LOAD_RELATIONS)
        if created_by is not None:
            stmt = stmt.where(Ticket.created_by == created_by)
        if status is not None:
            stmt = stmt.where(Ticket.status == status)
        if category_id is not None:
            stmt = stmt.where(Ticket.category_id == category_id)
        if assigned_to is not None:
            stmt = stmt.where(Ticket.assigned_to == assigned_to)
        stmt = stmt.order_by(Ticket.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, ticket: Ticket) -> Ticket:
        self.session.add(ticket)
        await self.session.flush()
        return await self.get(ticket.id)

    async def update(self, ticket: Ticket, changes: dict) -> Ticket:
        for field, value in changes.items():
            setattr(ticket, field, value)
        await self.session.flush()
        return await self.get(ticket.id)

    async def count_by_category(self, category_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Ticket).where(Ticket.category_id == category_id)
        )
        return result.scalar_one()


