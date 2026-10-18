import asyncio
import sys
import time

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from app.ai.triage.graph import build_triage_graph
from app.core.config import settings
from app.db.session import engine

USAGE = (
    "Usage:\n"
    "  python -m scripts.try_day12 start <ticket_id> <agent_id>\n"
    "  python -m scripts.try_day12 resume <thread_id> <approve|edit|reject> <agent_id> [text]"
)


def show(result: dict) -> None:
    for key in ("priority", "summary", "route", "can_answer", "draft_reply", "outcome"):
        if key in result:
            print(f"{key}: {result[key]}")
    if "articles" in result:
        print("articles:", [a["title"] for a in result["articles"]])
    if "__interrupt__" in result:
        print("PAUSED:", result["__interrupt__"])


async def main(args: list[str]) -> None:
    if len(args) < 3:
        raise SystemExit(USAGE)
    async with AsyncPostgresSaver.from_conn_string(
        settings.checkpoint_database_url
    ) as checkpointer:
        await checkpointer.setup()
        graph = build_triage_graph(checkpointer)

        if args[0] == "start":
            thread_id = f"test-{args[1]}-{int(time.time())}"
            config = {"configurable": {"thread_id": thread_id}}
            print("thread_id:", thread_id)
            result = await graph.ainvoke(
                {"run_id": 0, "ticket_id": int(args[1]), "started_by": int(args[2])},
                config,
            )
        else:
            thread_id = args[1]
            config = {"configurable": {"thread_id": thread_id}}
            decision = {
                "action": args[2],
                "text": args[4] if len(args) > 4 else None,
                "approver_id": int(args[3]),
            }
            result = await graph.ainvoke(Command(resume=decision), config)

        show(result)
        snapshot = await graph.aget_state(config)
        print("next:", snapshot.next)


async def run(args: list[str]) -> None:
    try:
        await main(args)
    finally:
        await engine.dispose()


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


asyncio.run(run(sys.argv[1:]))



# RUN: python -m scripts.try_day12 start <ticketA> <agentId>
# RUN: python -m scripts.try_day12 start 4 2

# RUN: python -m scripts.try_day12 resume <thread_id> <approve|edit|reject> <agent_id> [text]
# RUN: python -m scripts.try_day12 resume "test-4-1792341044" edit 2 "Please reinstall the VPN client, then reconnect"