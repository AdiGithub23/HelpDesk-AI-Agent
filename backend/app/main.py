from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.exceptions import (
    AIProviderError,
    AppError,
    AuthenticationError,
    ConflictError,
    InvalidTransitionError,
    NotFoundError,
    PermissionDeniedError,
)
from app.db.session import engine

STATUS_CODES = {
    AuthenticationError: 401,
    PermissionDeniedError: 403,
    NotFoundError: 404,
    ConflictError: 409,
    InvalidTransitionError: 409,
    AIProviderError: 502,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()      # close the connection pool when the app stops


app = FastAPI(title="Helpdesk API", lifespan=lifespan)
app.include_router(api_router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    status_code = STATUS_CODES.get(type(exc), 400)
    headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
    return JSONResponse(
        status_code=status_code, content={"detail": str(exc)}, headers=headers
    )


