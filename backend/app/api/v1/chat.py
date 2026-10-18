from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, SessionDep
from app.schemas.chat import ChatSessionRead, MessageCreate, MessageRead
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat/sessions", tags=["chat"])


@router.post("", response_model=ChatSessionRead, status_code=201)
async def create_session(session: SessionDep, user: CurrentUser):
    return await ChatService(session).create_session(user)


@router.get("", response_model=list[ChatSessionRead])
async def list_sessions(
    session: SessionDep,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await ChatService(session).list_sessions(user, limit=limit, offset=offset)


@router.get("/{chat_id}/messages", response_model=list[MessageRead])
async def list_messages(chat_id: int, session: SessionDep, user: CurrentUser):
    return await ChatService(session).list_messages(user, chat_id)


@router.post("/{chat_id}/messages", response_model=MessageRead, status_code=201)
async def ask(chat_id: int, data: MessageCreate, session: SessionDep, user: CurrentUser):
    return await ChatService(session).ask(user, chat_id, data)
