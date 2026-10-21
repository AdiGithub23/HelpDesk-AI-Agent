from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import TicketPriority, TriageStatus


class TriageRun(Base):
    __tablename__ = "triage_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    started_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[TriageStatus] = mapped_column(
        Enum(TriageStatus, name="triage_status"), default=TriageStatus.running
    )
    # reuses the existing ticket_priority type, so it must not be created again
    suggested_priority: Mapped[TicketPriority | None] = mapped_column(
        PGEnum(TicketPriority, name="ticket_priority", create_type=False)
    )
    summary: Mapped[str | None] = mapped_column(Text)
    draft_reply: Mapped[str | None] = mapped_column(Text)
    sources: Mapped[list | None] = mapped_column(JSON)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    final_reply: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )




