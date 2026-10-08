import asyncio

from sqlalchemy import select

from app.core.exceptions import AppError
from app.db.session import AsyncSessionLocal, engine
from app.models import User
from app.models.enums import TicketStatus, UserRole
from app.schemas.category import CategoryCreate
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketRead
from app.schemas.comment import CommentCreate, CommentRead
from app.services.category_service import CategoryService
from app.services.ticket_service import TicketService
from app.services.comment_service import CommentService


async def get_or_create_user(session, email, role):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(email=email, full_name=email.split("@")[0],
                    hashed_password="not-a-real-hash", role=role)
        session.add(user)
        await session.commit()
    return user


async def expect_error(label, coro):
    try:
        await coro
        print(f"FAIL  {label}: no error was raised")
    except AppError as e:
        print(f"OK    {label}: {type(e).__name__} - {e}")


async def main():
    async with AsyncSessionLocal() as session:
        employee = await get_or_create_user(session, "emp@test.com", UserRole.employee)
        agent = await get_or_create_user(session, "agent@test.com", UserRole.agent)

        categories = CategoryService(session)
        tickets = TicketService(session)
        comments = CommentService(session)

        await expect_error("duplicate category",
                           categories.create_category(CategoryCreate(name="VPN")))  # run twice to see this
        existing = [c for c in await categories.list_categories() if c.name == "VPN"]
        category = existing[0] if existing else await categories.create_category(CategoryCreate(name="VPN"))

        ticket = await tickets.create_ticket(
            employee, TicketCreate(title="VPN down", description="Cannot connect", category_id=category.id))
        print("created:", TicketRead.model_validate(ticket).model_dump_json(indent=2))

        await expect_error("employee open -> in_progress",
                           tickets.change_status(employee, ticket.id, TicketStatus.in_progress))
        await expect_error("agent open -> resolved",
                           tickets.change_status(agent, ticket.id, TicketStatus.resolved))
        await expect_error("assign to an employee",
                           tickets.assign_ticket(agent, ticket.id, employee.id))
        await expect_error("delete category in use",
                           categories.delete_category(category.id))

        t = await tickets.change_status(agent, ticket.id, TicketStatus.in_progress)
        print("agent moved it to:", t.status.value)
        t = await tickets.assign_ticket(agent, ticket.id, agent.id)
        print("assigned to:", t.assignee.email)

        # --- comments (rule 3) ---
        await comments.add_comment(employee, ticket.id, CommentCreate(body="Still broken"))
        await comments.add_comment(agent, ticket.id, CommentCreate(body="Checking logs", is_internal=True))
        await expect_error("employee internal note",
                           comments.add_comment(employee, ticket.id, CommentCreate(body="x", is_internal=True)))

        emp_list = await comments.list_comments(employee, ticket.id)
        agent_list = await comments.list_comments(agent, ticket.id)
        print("employee sees:", [c.body for c in emp_list])      # no internal note
        print("agent sees:", [c.body for c in agent_list])       # both
        print(CommentRead.model_validate(agent_list[0]).model_dump_json(indent=2))

        # --- ownership and edit rules ---
        other = await get_or_create_user(session, "other@test.com", UserRole.employee)
        await expect_error("other employee reads my ticket",
                           tickets.get_ticket(other, ticket.id))
        await expect_error("employee edits non-open ticket",
                           tickets.update_ticket(employee, ticket.id, TicketUpdate(title="New")))
        mine = await tickets.list_tickets(other)
        print("other employee's tickets:", len(mine))            # expect 0


async def run():
    try:
        await main()
    finally:
        await engine.dispose()

asyncio.run(run())



# RUN: python -m scripts.try_day3