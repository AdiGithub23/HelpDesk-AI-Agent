from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermissionDeniedError
from app.models import Comment, User
from app.models.enums import UserRole
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate
from app.services.ticket_service import TicketService


class CommentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.comments = CommentRepository(session)
        self.ticket_service = TicketService(session)

    async def add_comment(
        self, user: User, ticket_id: int, data: CommentCreate
    ) -> Comment:
        await self.ticket_service.get_ticket(user, ticket_id)       # Ownership rule: raises NotFoundError / PermissionDeniedError

        if data.is_internal and user.role != UserRole.agent:
            raise PermissionDeniedError("Only agents can leave internal notes")

        comment = await self.comments.add(
            Comment(
                ticket_id=ticket_id,
                author_id=user.id,
                body=data.body,
                is_internal=data.is_internal,
            )
        )
        await self.session.commit()
        return comment

    async def list_comments(self, user: User, ticket_id: int) -> list[Comment]:
        await self.ticket_service.get_ticket(user, ticket_id)
        include_internal = user.role == UserRole.agent  # rule 3
        return await self.comments.list_by_ticket(ticket_id, include_internal)
