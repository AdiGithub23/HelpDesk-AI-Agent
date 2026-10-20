from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TriageRun
from app.models.enums import TriageStatus

ACTIVE_STATUSES = (TriageStatus.running, TriageStatus.awaiting_review)


class TriageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, run_id: int) -> TriageRun | None:
        return await self.session.get(TriageRun, run_id)

    async def list_by_ticket(self, ticket_id: int) -> list[TriageRun]:
        stmt = (
            select(TriageRun)
            .where(TriageRun.ticket_id == ticket_id)
            .order_by(TriageRun.created_at.desc(), TriageRun.id.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_for_ticket(self, ticket_id: int) -> TriageRun | None:
        stmt = select(TriageRun).where(
            TriageRun.ticket_id == ticket_id,
            TriageRun.status.in_(ACTIVE_STATUSES),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def add(self, run: TriageRun) -> TriageRun:
        self.session.add(run)
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def update(self, run: TriageRun, changes: dict) -> TriageRun:
        for field, value in changes.items():
            setattr(run, field, value)
        await self.session.flush()
        await self.session.refresh(run)   # reloads the DB-generated updated_at
        return run

    async def claim_for_decision(self, run_id: int) -> bool:
        """Atomically flip awaiting_review -> running. True only for the one caller who wins."""
        result = await self.session.execute(
            update(TriageRun)
            .where(
                TriageRun.id == run_id,
                TriageRun.status == TriageStatus.awaiting_review,
            )
            .values(status=TriageStatus.running)
        )
        await self.session.flush()
        return result.rowcount == 1

