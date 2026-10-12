from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.assistant import run_assistant
from app.core.exceptions import NotFoundError
from app.models import ChatSession, Message, User
from app.models.enums import MessageRole
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import MessageCreate

HISTORY_LIMIT = 10


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.chats = ChatRepository(session)

    async def create_session(self, user: User) -> ChatSession:
        chat = await self.chats.add_chat(ChatSession(user_id=user.id))
        await self.session.commit()
        return chat

    async def list_sessions(self, user: User, *, limit: int = 20, offset: int = 0) -> list[ChatSession]:
        return await self.chats.list_chats(user.id, limit, offset)

    async def list_messages(self, user: User, chat_id: int) -> list[Message]:
        chat = await self._get_owned(user, chat_id)
        return await self.chats.list_messages(chat.id)

    async def ask(self, user: User, chat_id: int, data: MessageCreate) -> Message:
        chat = await self._get_owned(user, chat_id)
        recent = await self.chats.list_recent_messages(chat.id, HISTORY_LIMIT)
        history = [(m.role.value, m.content) for m in recent]

        answer, sources = await run_assistant(self.session, user, history, data.content)

        await self.chats.add_message(
            Message(session_id=chat.id, role=MessageRole.user, content=data.content)
        )
        assistant_message = await self.chats.add_message(
            Message(
                session_id=chat.id,
                role=MessageRole.assistant,
                content=answer,
                sources=sources or None,
            )
        )
        title = data.content[:60] if chat.title is None else None
        await self.chats.touch_chat(chat.id, title)
        await self.session.commit()
        return assistant_message

    async def _get_owned(self, user: User, chat_id: int) -> ChatSession:
        """Rule 16: someone else's session looks like it doesn't exist."""
        chat = await self.chats.get_chat(chat_id)
        if chat is None or chat.user_id != user.id:
            raise NotFoundError("Chat session not found")
        return chat

