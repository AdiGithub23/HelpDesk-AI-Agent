from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.comment import CommentCreate, CommentRead
from app.services.comment_service import CommentService

router = APIRouter(prefix="/tickets/{ticket_id}/comments", tags=["comments"])


@router.post("", response_model=CommentRead, status_code=201)
async def add_comment(
    ticket_id: int, data: CommentCreate, session: SessionDep, user: CurrentUser
):
    return await CommentService(session).add_comment(user, ticket_id, data)


@router.get("", response_model=list[CommentRead])
async def list_comments(ticket_id: int, session: SessionDep, user: CurrentUser):
    return await CommentService(session).list_comments(user, ticket_id)
