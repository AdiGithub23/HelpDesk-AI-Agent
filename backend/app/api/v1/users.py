from fastapi import APIRouter

from app.api.deps import AgentUser, CurrentUser, SessionDep, SuperiorUser
from app.models.enums import UserRole
from app.schemas.user import MeRead, UserActiveUpdate, UserRead, UserRoleUpdate
from app.services.user_service import UserService
from app.core.security import is_superior_agent


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=MeRead)
async def read_me(user: CurrentUser):
    return MeRead(
        **UserRead.model_validate(user).model_dump(), is_superior=is_superior_agent(user)
    )

@router.get("", response_model=list[UserRead])
async def list_users(session: SessionDep, user: AgentUser, role: UserRole | None = None):
    return await UserService(session).list_users(user, role)

@router.patch("/{user_id}/role", response_model=UserRead)
async def change_role(
    user_id: int, data: UserRoleUpdate, session: SessionDep, user: SuperiorUser
):
    return await UserService(session).change_role(user, user_id, data.role)

@router.patch("/{user_id}/active", response_model=UserRead)
async def set_active(
    user_id: int, data: UserActiveUpdate, session: SessionDep, user: SuperiorUser
):
    return await UserService(session).set_active(user, user_id, data.is_active)

