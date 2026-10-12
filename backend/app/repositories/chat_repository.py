from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChatSession, Message


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_chat(self, chat: ChatSession) -> ChatSession:
        self.session.add(chat)
        await self.session.flush()
        await self.session.refresh(chat)   # loads the DB-generated timestamps
        return chat

    async def get_chat(self, chat_id: int) -> ChatSession | None:
        return await self.session.get(ChatSession, chat_id)

    async def list_chats(self, user_id: int, limit: int, offset: int) -> list[ChatSession]:
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc(), ChatSession.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def touch_chat(self, chat_id: int, title: str | None = None) -> None:
        values = {"updated_at": func.now()}
        if title:
            values["title"] = title
        await self.session.execute(
            update(ChatSession).where(ChatSession.id == chat_id).values(**values)
        )
        await self.session.flush()

    async def add_message(self, message: Message) -> Message:
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def list_messages(self, chat_id: int) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.session_id == chat_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent_messages(self, chat_id: int, limit: int) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.session_id == chat_id)
            .order_by(Message.id.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(reversed(result.scalars().all()))   # oldest first

