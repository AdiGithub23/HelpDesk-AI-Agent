from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MessageRole


class SourceRead(BaseModel):
    article_id: int
    title: str


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: MessageRole
    content: str
    sources: list[SourceRead] | None
    created_at: datetime


class ChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    created_at: datetime
    updated_at: datetime

