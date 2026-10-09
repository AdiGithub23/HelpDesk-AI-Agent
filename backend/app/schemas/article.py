from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ArticleStatus
from app.schemas.category import CategoryRead
from app.schemas.user import UserRead


class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1)
    category_id: int


class ArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    body: str | None = Field(default=None, min_length=1)
    category_id: int | None = None


class ArticleStatusUpdate(BaseModel):
    status: ArticleStatus


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    status: ArticleStatus
    category: CategoryRead
    author: UserRead
    created_at: datetime
    updated_at: datetime



