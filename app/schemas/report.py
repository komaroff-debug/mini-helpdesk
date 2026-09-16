from pydantic import BaseModel


class AvgResolutionTimeOut(BaseModel):
    group: str
    avg_hours: float | None
    resolved_count: int


class OverdueTicketOut(BaseModel):
    id: int
    title: str
    status: str
    hours_in_status: float


class TicketsByStatusOut(BaseModel):
    status: str
    count: int
