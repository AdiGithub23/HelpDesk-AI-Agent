from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END
from langgraph.types import interrupt
from pydantic import BaseModel

from app.ai.llm import get_llm
from app.ai.prompts import CLASSIFY_PROMPT, DRAFT_PROMPT
from app.ai.tools import MAX_DISTANCE
from app.ai.triage.state import TriageState
from app.core.exceptions import AIProviderError, ConflictError, PermissionDeniedError
from app.db.session import AsyncSessionLocal
from app.models.enums import UserRole
from app.schemas.comment import CommentCreate
from app.services.comment_service import CommentService
from app.services.indexing_service import IndexingService
from app.services.ticket_service import TicketService
from app.services.user_service import UserService


class Classification(BaseModel):
    priority: Literal["low", "medium", "high"]
    summary: str


class Draft(BaseModel):
    can_answer: bool
    reply: str = ""


async def _ask(schema: type[BaseModel], system: str, human: str):
    """One structured LLM call. Any provider failure becomes AIProviderError."""
    try:
        structured = get_llm().with_structured_output(schema)
        return await structured.ainvoke(
            [SystemMessage(content=system), HumanMessage(content=human)]
        )
    except Exception as e:
        raise AIProviderError("Chat model request failed") from e


def _ticket_text(state: TriageState) -> str:
    return (
        f"Title: {state['title']}\n"
        f"Category: {state['category_name']}\n"
        f"Description: {state['description']}"
    )


# ---- nodes: each returns only the keys it changes ----

async def load_ticket(state: TriageState) -> dict:
    async with AsyncSessionLocal() as session:
        agent = await UserService(session).get_user(state["started_by"])
        ticket = await TicketService(session).get_ticket(agent, state["ticket_id"])
        return {
            "title": ticket.title,
            "description": ticket.description,
            "category_name": ticket.category.name,
        }


async def classify(state: TriageState) -> dict:
    result = await _ask(Classification, CLASSIFY_PROMPT, _ticket_text(state))
    return {"priority": result.priority, "summary": result.summary}


async def retrieve(state: TriageState) -> dict:
    async with AsyncSessionLocal() as session:
        hits = await IndexingService(session).search(
            f"{state['title']}\n{state['description']}", k=4
        )
    return {
        "articles": [
            {"article_id": h.article_id, "title": h.title, "content": h.content}
            for h in hits
            if h.distance <= MAX_DISTANCE
        ]
    }


async def decide(state: TriageState) -> dict:
    return {"route": "auto_reply" if state.get("articles") else "agent"}


async def write_draft(state: TriageState) -> dict:
    articles = "\n\n".join(
        f"[Article #{a['article_id']}: {a['title']}]\n{a['content']}"
        for a in state["articles"]
    )
    result = await _ask(
        Draft, DRAFT_PROMPT, f"{_ticket_text(state)}\n\nArticles:\n{articles}"
    )
    reply = result.reply.strip()
    can_answer = result.can_answer and bool(reply)
    return {"can_answer": can_answer, "draft_reply": reply if can_answer else ""}


async def human_review(state: TriageState) -> dict:
    # Runs twice (pause, then resume): nothing irreversible may happen before this line.
    decision = interrupt(
        {"ticket_id": state["ticket_id"], "draft_reply": state["draft_reply"]}
    )
    update: dict = {"decision": decision}
    if decision["action"] == "reject":
        update["outcome"] = "rejected"
    return update


async def send_reply(state: TriageState) -> dict:
    decision = state["decision"]
    text = (
        (decision.get("text") or "")
        if decision["action"] == "edit"
        else state["draft_reply"]
    ).strip()
    if not text:
        raise ConflictError("The reply is empty")
    async with AsyncSessionLocal() as session:
        approver = await UserService(session).get_user(decision["approver_id"])
        if approver.role != UserRole.agent or not approver.is_active:
            raise PermissionDeniedError("Only an active agent can approve a reply")
        await CommentService(session).add_comment(
            approver, state["ticket_id"], CommentCreate(body=text, is_internal=False)
        )
    return {"outcome": "sent"}


async def prepare_handoff(state: TriageState) -> dict:
    return {"outcome": "handed_off"}


# ---- routing functions: read state, return the next node's name ----

def route_after_decide(state: TriageState) -> str:
    return "write_draft" if state["route"] == "auto_reply" else "prepare_handoff"


def route_after_draft(state: TriageState) -> str:
    return "human_review" if state["can_answer"] else "prepare_handoff"


def route_after_review(state: TriageState) -> str:
    return "send_reply" if state["decision"]["action"] in ("approve", "edit") else END




