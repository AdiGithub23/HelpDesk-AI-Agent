from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm import get_llm
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.tools import build_tools
from app.core.exceptions import AIProviderError
from app.models import User

MAX_STEPS = 4
FALLBACK = "Sorry, I could not complete that request. Please try again."


def _text(message) -> str:
    content = message.content
    if isinstance(content, str):
        return content.strip()
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts).strip()


async def run_assistant(
    session: AsyncSession,
    user: User,
    history: list[tuple[str, str]],
    question: str,
) -> tuple[str, list[dict]]:
    """Returns (answer, sources). history is a list of (role, content), oldest first."""
    sources: dict[int, str] = {}
    tools = build_tools(session, user, sources)
    tools_by_name = {t.name: t for t in tools}
    llm = get_llm().bind_tools(tools)

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for role, content in history:
        messages.append(HumanMessage(content=content) if role == "user" else AIMessage(content=content))
    messages.append(HumanMessage(content=question))

    for _ in range(MAX_STEPS):
        try:
            reply = await llm.ainvoke(messages)
        except Exception as e:
            raise AIProviderError("Chat model request failed") from e
        messages.append(reply)

        if not reply.tool_calls:
            answer = _text(reply) or FALLBACK
            return answer, [{"article_id": i, "title": t} for i, t in sources.items()]

        for call in reply.tool_calls:   # one after another: a session can't run queries in parallel
            tool = tools_by_name.get(call["name"])
            result = await tool.ainvoke(call["args"]) if tool else "Unknown tool."
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    return FALLBACK, []




