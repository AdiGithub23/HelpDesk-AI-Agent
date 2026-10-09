from fastapi import APIRouter

from app.api.deps import AgentUser, CurrentUser, SessionDep
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(session: SessionDep, user: CurrentUser):
    return await CategoryService(session).list_categories()


@router.post("", response_model=CategoryRead, status_code=201)
async def create_category(data: CategoryCreate, session: SessionDep, user: AgentUser):
    return await CategoryService(session).create_category(data)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int, data: CategoryUpdate, session: SessionDep, user: AgentUser
):
    return await CategoryService(session).update_category(category_id, data)


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, session: SessionDep, user: AgentUser):
    await CategoryService(session).delete_category(category_id)
