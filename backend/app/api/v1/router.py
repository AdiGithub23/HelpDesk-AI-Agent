from fastapi import APIRouter
    
from app.api.v1 import articles, auth, categories, comments, tickets, users, chat, triage, speech


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(tickets.router)
api_router.include_router(comments.router)
api_router.include_router(articles.router)
api_router.include_router(chat.router)
api_router.include_router(triage.router)
api_router.include_router(speech.router)