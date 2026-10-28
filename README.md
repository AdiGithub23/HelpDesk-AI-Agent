# HelpDesk-AI-Agent

An internal helpdesk for a small company: tickets, comments, a knowledge base, an AI chat assistant that answers from published articles, and an AI-assisted triage workflow with human approval.

**Stack:** FastAPI, SQLAlchemy 2.0 (async), Neon Postgres + pgvector, Alembic, JWT, LangChain, LangGraph, Google Gemini (free tier).

## Layers
1. **Software foundation:** users and roles, categories, tickets, comments, articles.
2. **RAG chat:** chat sessions with history. The assistant searches published articles by meaning and can look up the user's own tickets.
3. **Triage workflow (LangGraph):** an agent starts a run on a ticket. The graph classifies it and searches the knowledge base in parallel, drafts a reply, and pauses. The agent approves, edits or rejects it. Only then is a comment posted.

The design document describes every rule and decision.

## Setup (run everything from `backend/`)
```
python -m venv .venv                # Python 3.12 (3.11 or later is required)
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env              # then fill in the values
alembic upgrade head
python -m scripts.seed_agent        # creates the first agent from .env
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs.

## Scripts
- `scripts/seed_agent.py`: creates the first agent.
- `scripts/reindex_articles.py`: indexes published articles that were created before indexing existed.
- `scripts/try_day8.py`, `scripts/try_day12.py`: development helpers for article search and the triage graph.

On Windows, scripts that use the triage checkpointer must set the selector event-loop policy (see `try_day12.py`).

## Known limits
No automatic triage, refresh tokens, tests, Docker or request logging yet. See "Future Improvements" in the design document.
