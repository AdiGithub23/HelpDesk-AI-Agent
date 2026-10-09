from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AgentUser, CurrentUser, SessionDep
from app.models.enums import ArticleStatus
from app.schemas.article import (
    ArticleCreate,
    ArticleRead,
    ArticleStatusUpdate,
    ArticleUpdate,
)
from app.services.article_service import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[ArticleRead])
async def list_articles(
    session: SessionDep,
    user: CurrentUser,
    category_id: int | None = None,
    status: ArticleStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await ArticleService(session).list_articles(
        user, category_id=category_id, status=status, limit=limit, offset=offset
    )


@router.get("/{article_id}", response_model=ArticleRead)
async def get_article(article_id: int, session: SessionDep, user: CurrentUser):
    return await ArticleService(session).get_article(user, article_id)


@router.post("", response_model=ArticleRead, status_code=201)
async def create_article(data: ArticleCreate, session: SessionDep, user: AgentUser):
    return await ArticleService(session).create_article(user, data)


@router.patch("/{article_id}", response_model=ArticleRead)
async def update_article(
    article_id: int, data: ArticleUpdate, session: SessionDep, user: AgentUser
):
    return await ArticleService(session).update_article(article_id, data)


@router.patch("/{article_id}/status", response_model=ArticleRead)
async def change_status(
    article_id: int, data: ArticleStatusUpdate, session: SessionDep, user: AgentUser
):
    return await ArticleService(session).change_status(article_id, data.status)


@router.delete("/{article_id}", status_code=204)
async def delete_article(article_id: int, session: SessionDep, user: AgentUser):
    await ArticleService(session).delete_article(article_id)

