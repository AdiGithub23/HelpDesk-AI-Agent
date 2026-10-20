from langgraph.types import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.models import TriageRun, User
from app.models.enums import TicketPriority, TriageStatus, UserRole
from app.repositories.triage_repository import TriageRepository
from app.schemas.triage import TriageDecision
from app.services.ticket_service import TicketService

OUTCOME_STATUS = {
    "sent": TriageStatus.sent,
    "rejected": TriageStatus.rejected,
    "handed_off": TriageStatus.handed_off,
}


def _config(run_id: int) -> dict:
    return {"configurable": {"thread_id": str(run_id)}}


def _changes_from_result(result: dict) -> dict:
    """Copies the graph's final (or paused) state into the columns of the run row."""
    draft = result.get("draft_reply") or None
    priority = result.get("priority")
    changes: dict = {
        "suggested_priority": TicketPriority(priority) if priority else None,
        "summary": result.get("summary"),
        "draft_reply": draft,
        "sources": (
            [{"article_id": a["article_id"], "title": a["title"]} for a in result.get("articles", [])]
            if draft
            else None
        ),
    }
    if "__interrupt__" in result:
        changes["status"] = TriageStatus.awaiting_review
        return changes

    outcome = result["outcome"]
    changes["status"] = OUTCOME_STATUS[outcome]
    decision = result.get("decision")
    if decision:
        changes["decided_by"] = decision["approver_id"]
        if outcome == "sent":
            changes["final_reply"] = (
                decision.get("text") if decision["action"] == "edit" else draft
            )
    return changes


class TriageService:
    def __init__(self, session: AsyncSession, graph):
        self.session = session
        self.graph = graph
        self.runs = TriageRepository(session)
        self.tickets = TicketService(session)

    async def start(self, user: User, ticket_id: int) -> TriageRun:
        await self.tickets.get_ticket(user, ticket_id)          # exists (rule 19: agents only, by the route)
        if await self.runs.get_active_for_ticket(ticket_id):    # rule 25
            raise ConflictError("This ticket already has an active triage run")

        run = await self.runs.add(
            TriageRun(ticket_id=ticket_id, started_by=user.id, status=TriageStatus.running)
        )
        await self.session.commit()

        try:
            result = await self.graph.ainvoke(
                {"run_id": run.id, "ticket_id": ticket_id, "started_by": user.id},
                _config(run.id),
            )
        except Exception as e:
            await self.runs.update(
                run,
                {"status": TriageStatus.failed, "error": f"{type(e).__name__}: {e}"[:500]},
            )
            await self.session.commit()
            raise

        run = await self.runs.update(run, _changes_from_result(result))
        await self.session.commit()
        return run

    async def decide(self, user: User, run_id: int, data: TriageDecision) -> TriageRun:
        run = await self._get_or_404(run_id)
        if user.role != UserRole.agent or not user.is_active:     # approver check, before resuming
            raise PermissionDeniedError("Only an active agent can decide")
        if not await self.runs.claim_for_decision(run_id):        # rule 23, atomic
            raise ConflictError("This run is not waiting for a decision")
        await self.session.commit()

        config = _config(run_id)
        try:
            snapshot = await self.graph.aget_state(config)
            if snapshot.next == ("send_reply",):
                # an earlier attempt failed inside send_reply: continue with the SAVED decision
                result = await self.graph.ainvoke(None, config)
            else:
                resume = {"action": data.action, "text": data.text, "approver_id": user.id}
                result = await self.graph.ainvoke(Command(resume=resume), config)
        except Exception:
            await self.runs.update(run, {"status": TriageStatus.awaiting_review})
            await self.session.commit()
            raise

        run = await self.runs.update(run, _changes_from_result(result))
        await self.session.commit()
        return run

    async def list_runs(self, user: User, ticket_id: int) -> list[TriageRun]:
        await self.tickets.get_ticket(user, ticket_id)
        return await self.runs.list_by_ticket(ticket_id)

    async def get_run(self, run_id: int) -> TriageRun:
        return await self._get_or_404(run_id)

    async def _get_or_404(self, run_id: int) -> TriageRun:
        run = await self.runs.get(run_id)
        if run is None:
            raise NotFoundError("Triage run not found")
        return run

