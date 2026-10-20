from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import TicketPriority, TriageStatus
from app.schemas.chat import SourceRead


class TriageDecision(BaseModel):
    action: Literal["approve", "edit", "reject"]
    text: str | None = Field(default=None, max_length=5000)

    @model_validator(mode="after")
    def edit_needs_text(self):
        if self.action == "edit" and not (self.text or "").strip():
            raise ValueError("text is required when action is 'edit'")
        return self


class TriageRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    started_by: int
    status: TriageStatus
    suggested_priority: TicketPriority | None
    summary: str | None
    draft_reply: str | None
    sources: list[SourceRead] | None
    decided_by: int | None
    final_reply: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime



