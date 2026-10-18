from langgraph.graph import END, START, StateGraph

from app.ai.triage.nodes import (
    classify,
    decide,
    human_review,
    load_ticket,
    prepare_handoff,
    retrieve,
    route_after_decide,
    route_after_draft,
    route_after_review,
    send_reply,
    write_draft,
)
from app.ai.triage.state import TriageState


def build_triage_graph(checkpointer):
    builder = StateGraph(TriageState)

    builder.add_node("load_ticket", load_ticket)
    builder.add_node("classify", classify)
    builder.add_node("retrieve", retrieve)
    builder.add_node("decide", decide)
    builder.add_node("write_draft", write_draft)
    builder.add_node("human_review", human_review)
    builder.add_node("send_reply", send_reply)
    builder.add_node("prepare_handoff", prepare_handoff)

    builder.add_edge(START, "load_ticket")
    # parallel fan-out: both start after load_ticket
    builder.add_edge("load_ticket", "classify")
    builder.add_edge("load_ticket", "retrieve")
    # fan-in: decide waits for BOTH
    builder.add_edge(["classify", "retrieve"], "decide")

    builder.add_conditional_edges(
        "decide", route_after_decide, ["write_draft", "prepare_handoff"]
    )
    builder.add_conditional_edges(
        "write_draft", route_after_draft, ["human_review", "prepare_handoff"]
    )
    builder.add_conditional_edges(
        "human_review", route_after_review, ["send_reply", END]
    )

    builder.add_edge("send_reply", END)
    builder.add_edge("prepare_handoff", END)

    return builder.compile(checkpointer=checkpointer)



