from enum import Enum


class UserRole(str, Enum):
    employee = "employee"
    agent = "agent"


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ArticleStatus(str, Enum):
    draft = "draft"
    published = "published"
