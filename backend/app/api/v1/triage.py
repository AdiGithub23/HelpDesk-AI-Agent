from fastapi import APIRouter

from app.api.deps import AgentUser, SessionDep, TriageGraphDep
from app.schemas.triage import TriageDecision, TriageRunRead
from app.services.triage_service import TriageService

router = APIRouter(tags=["triage"])


@router.post("/tickets/{ticket_id}/triage-runs", response_model=TriageRunRead, status_code=201)
async def start_triage(
    ticket_id: int, session: SessionDep, user: AgentUser, graph: TriageGraphDep
):
    return await TriageService(session, graph).start(user, ticket_id)


@router.get("/tickets/{ticket_id}/triage-runs", response_model=list[TriageRunRead])
async def list_triage_runs(
    ticket_id: int, session: SessionDep, user: AgentUser, graph: TriageGraphDep
):
    return await TriageService(session, graph).list_runs(user, ticket_id)


@router.get("/triage-runs/{run_id}", response_model=TriageRunRead)
async def get_triage_run(
    run_id: int, session: SessionDep, user: AgentUser, graph: TriageGraphDep
):
    return await TriageService(session, graph).get_run(run_id)


@router.post("/triage-runs/{run_id}/decision", response_model=TriageRunRead)
async def decide_triage(
    run_id: int,
    data: TriageDecision,
    session: SessionDep,
    user: AgentUser,
    graph: TriageGraphDep,
):
    return await TriageService(session, graph).decide(user, run_id, data)
