from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermissionDeniedError
from app.core.security import is_superior_agent
from app.db.session import AsyncSessionLocal
from app.models import User
from app.models.enums import UserRole
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> User:
    return await AuthService(session).get_user_from_token(token)


CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_agent(user: CurrentUser) -> User:
    if user.role != UserRole.agent:
        raise PermissionDeniedError("Agents only")
    return user


AgentUser = Annotated[User, Depends(require_agent)]


def get_triage_graph(request: Request):
    return request.app.state.triage_graph


TriageGraphDep = Annotated[object, Depends(get_triage_graph)]


async def require_superior_agent(user: AgentUser) -> User:
    if not is_superior_agent(user):
        raise PermissionDeniedError("Only the superior agent can do this")
    return user


SuperiorUser = Annotated[User, Depends(require_superior_agent)]


def get_stt_model(request: Request):
    return request.app.state.stt_model


SttModelDep = Annotated[object, Depends(get_stt_model)]

