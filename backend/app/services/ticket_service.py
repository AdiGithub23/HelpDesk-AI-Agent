from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    InvalidTransitionError,
    NotFoundError,
    PermissionDeniedError,
)
from app.models import Ticket, User
from app.models.enums import TicketStatus, UserRole
from app.repositories.category_repository import CategoryRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.schemas.ticket import TicketCreate, TicketUpdate

AGENT_ONLY = {UserRole.agent}
OWNER_OR_AGENT = {UserRole.employee, UserRole.agent}

# (from, to) -> roles allowed. This IS the transition table from the design.
ALLOWED_TRANSITIONS = {
    (TicketStatus.open, TicketStatus.in_progress): AGENT_ONLY,
    (TicketStatus.in_progress, TicketStatus.resolved): AGENT_ONLY,
    (TicketStatus.resolved, TicketStatus.closed): OWNER_OR_AGENT,
    (TicketStatus.resolved, TicketStatus.in_progress): OWNER_OR_AGENT,
    (TicketStatus.open, TicketStatus.closed): AGENT_ONLY,
    (TicketStatus.in_progress, TicketStatus.closed): AGENT_ONLY,
}


class TicketService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tickets = TicketRepository(session)
        self.categories = CategoryRepository(session)
        self.users = UserRepository(session)

    async def create_ticket(self, user: User, data: TicketCreate) -> Ticket:
        if await self.categories.get(data.category_id) is None:
            raise NotFoundError("Category not found")
        ticket = await self.tickets.add(
            Ticket(
                title=data.title,
                description=data.description,
                priority=data.priority,
                category_id=data.category_id,
                created_by=user.id,
            )
        )
        await self.session.commit()
        return ticket

    async def get_ticket(self, user: User, ticket_id: int) -> Ticket:
        return await self._get_accessible(user, ticket_id)

    async def list_tickets(
        self,
        user: User,
        *,
        status: TicketStatus | None = None,
        category_id: int | None = None,
        assigned_to: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Ticket]:
        created_by = None
        if user.role == UserRole.employee:
            created_by = user.id       # employees only ever see their own
            assigned_to = None         # the assignee filter is agent-only
        return await self.tickets.list(
            created_by=created_by,
            status=status,
            category_id=category_id,
            assigned_to=assigned_to,
            limit=limit,
            offset=offset,
        )

    async def update_ticket(self, user: User, ticket_id: int, data: TicketUpdate) -> Ticket:
        ticket = await self._get_accessible(user, ticket_id)
        if user.role == UserRole.employee and ticket.status != TicketStatus.open:
            raise PermissionDeniedError("You can only edit a ticket while it is open")
        changes = {k: v for k, v in data.model_dump(exclude_unset=True).items()
                   if v is not None}
        if "category_id" in changes:
            if await self.categories.get(changes["category_id"]) is None:
                raise NotFoundError("Category not found")
        ticket = await self.tickets.update(ticket, changes)
        await self.session.commit()
        return ticket

    async def change_status(self, user: User, ticket_id: int, new_status: TicketStatus) -> Ticket:
        ticket = await self._get_accessible(user, ticket_id)
        allowed_roles = ALLOWED_TRANSITIONS.get((ticket.status, new_status))
        if allowed_roles is None:
            raise InvalidTransitionError(
                f"Cannot move from {ticket.status.value} to {new_status.value}"
            )
        if user.role not in allowed_roles:
            raise PermissionDeniedError("You are not allowed to make this change")
        ticket = await self.tickets.update(ticket, {"status": new_status})
        await self.session.commit()
        return ticket

    async def assign_ticket(self, user: User, ticket_id: int, assignee_id: int) -> Ticket:
        ticket = await self._get_accessible(user, ticket_id)
        assignee = await self.users.get(assignee_id)
        if assignee is None:
            raise NotFoundError("User not found")
        if assignee.role != UserRole.agent:
            raise PermissionDeniedError("A ticket can only be assigned to an agent")
        if not assignee.is_active:
            raise ConflictError("Cannot assign a ticket to a deactivated user")
        ticket = await self.tickets.update(ticket, {"assigned_to": assignee_id})
        await self.session.commit()
        return ticket

    async def _get_accessible(self, user: User, ticket_id: int) -> Ticket:
        """Ownership rule: agents see everything, employees only their own."""
        ticket = await self.tickets.get(ticket_id)
        if ticket is None:
            raise NotFoundError("Ticket not found")
        if user.role != UserRole.agent and ticket.created_by != user.id:
            raise PermissionDeniedError("This is not your ticket")
        return ticket



