from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketPriority, TicketStatus
from app.schemas.comment import CommentOut


class TicketCreate(BaseModel):
    title: str
    description: str
    category_id: int | None = None
    priority: TicketPriority = TicketPriority.medium


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assigned_to: int | None = None
    category_id: int | None = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: str
    priority: str
    category_id: int | None
    created_by: int
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime


class TicketDetailOut(TicketOut):
    comments: list[CommentOut] = Field(default_factory=list)


class StatusHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    old_status: str | None
    new_status: str
    changed_by: int
    changed_at: datetime


class TicketListOut(BaseModel):
    items: list[TicketOut]
    total: int
    page: int
    size: int
