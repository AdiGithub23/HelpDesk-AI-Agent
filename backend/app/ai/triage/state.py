from typing import Literal, TypedDict


class ArticleRef(TypedDict):
    article_id: int
    title: str
    content: str


class Decision(TypedDict):
    action: Literal["approve", "edit", "reject"]
    text: str | None
    approver_id: int


class TriageState(TypedDict, total=False):
    # inputs
    run_id: int
    ticket_id: int
    started_by: int
    # load_ticket
    title: str
    description: str
    category_name: str
    # classify
    priority: str
    summary: str
    # retrieve
    articles: list[ArticleRef]
    # decide
    route: str
    # draft_reply
    can_answer: bool
    draft_reply: str
    # human_review
    decision: Decision
    # send_reply / prepare_handoff / human_review
    outcome: str

