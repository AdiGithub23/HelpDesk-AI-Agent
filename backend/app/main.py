from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

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
from app.ai.triage.checkpointer import create_checkpoint_pool
from app.ai.triage.graph import build_triage_graph

import logging

logger = logging.getLogger("uvicorn.error")

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
    pool = create_checkpoint_pool()
    await pool.open()
    try:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()                                  # creates checkpointer tables if they don't exist
        app.state.triage_graph = build_triage_graph(checkpointer)   # built once
        yield
    finally:
        await pool.close()
        await engine.dispose()


app = FastAPI(title="Helpdesk API", lifespan=lifespan)
app.include_router(api_router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    status_code = STATUS_CODES.get(type(exc), 400)
    if status_code >= 500:
        logger.error("%s: %s", type(exc).__name__, exc, exc_info=exc)
    headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
    return JSONResponse(
        status_code=status_code, content={"detail": str(exc)}, headers=headers
    )

