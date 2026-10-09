from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AgentUser, CurrentUser, SessionDep
from app.models.enums import TicketStatus
from app.schemas.ticket import (
    TicketAssign,
    TicketCreate,
    TicketRead,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketRead, status_code=201)
async def create_ticket(data: TicketCreate, session: SessionDep, user: CurrentUser):
    return await TicketService(session).create_ticket(user, data)


@router.get("", response_model=list[TicketRead])
async def list_tickets(
    session: SessionDep,
    user: CurrentUser,
    status: TicketStatus | None = None,
    category_id: int | None = None,
    assigned_to: int | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await TicketService(session).list_tickets(
        user,
        status=status,
        category_id=category_id,
        assigned_to=assigned_to,
        limit=limit,
        offset=offset,
    )


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket(ticket_id: int, session: SessionDep, user: CurrentUser):
    return await TicketService(session).get_ticket(user, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketRead)
async def update_ticket(
    ticket_id: int, data: TicketUpdate, session: SessionDep, user: CurrentUser
):
    return await TicketService(session).update_ticket(user, ticket_id, data)


@router.patch("/{ticket_id}/status", response_model=TicketRead)
async def change_status(
    ticket_id: int, data: TicketStatusUpdate, session: SessionDep, user: CurrentUser
):
    return await TicketService(session).change_status(user, ticket_id, data.status)


@router.put("/{ticket_id}/assignee", response_model=TicketRead)
async def assign_ticket(
    ticket_id: int, data: TicketAssign, session: SessionDep, user: AgentUser
):
    return await TicketService(session).assign_ticket(user, ticket_id, data.assignee_id)


