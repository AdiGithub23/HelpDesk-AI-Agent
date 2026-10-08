from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserRead


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)
    is_internal: bool = False


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    body: str
    is_internal: bool
    ticket_id: int
    author: UserRead
    created_at: datetime



