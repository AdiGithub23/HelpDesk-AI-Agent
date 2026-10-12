from langchain_core.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models.enums import TicketStatus
from app.services.indexing_service import IndexingService
from app.services.ticket_service import TicketService

MAX_DISTANCE = 0.40   # starting value from the Day 8 test distances; tune later


def build_tools(session: AsyncSession, user: User, sources: dict[int, str]) -> list:
    """Tools are built per request: session and user are fixed, the model can't change them."""

    @tool
    async def search_articles(query: str) -> str:
        """Search the company knowledge base (published how-to guides and policies) by meaning.
        Pass a complete, standalone question or phrase, never a vague follow-up fragment."""
        hits = await IndexingService(session).search(query, k=4)
        hits = [h for h in hits if h.distance <= MAX_DISTANCE]
        if not hits:
            return "No relevant articles found."
        for h in hits:
            sources[h.article_id] = h.title
        return "\n\n".join(f"[Article #{h.article_id}: {h.title}]\n{h.content}" for h in hits)

    @tool
    async def list_my_tickets(status: str | None = None, limit: int = 5) -> str:
        """List the current user's own support tickets, newest first.
        Optional status filter: open, in_progress, resolved or closed."""
        status_filter = None
        if status:
            try:
                status_filter = TicketStatus(status)
            except ValueError:
                return "Invalid status. Use open, in_progress, resolved or closed."
        tickets = await TicketService(session).list_tickets(
            user, status=status_filter, limit=max(1, min(limit, 10))
        )
        if not tickets:
            return "You have no tickets."
        return "\n".join(
            f"#{t.id} | {t.status.value} | {t.priority.value} | {t.title} | category: {t.category.name}"
            for t in tickets
        )

    return [search_articles, list_my_tickets]


