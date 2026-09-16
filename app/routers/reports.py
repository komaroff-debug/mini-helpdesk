from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.status_history import StatusHistory
from app.models.ticket import Ticket
from app.schemas.report import AvgResolutionTimeOut, OverdueTicketOut, TicketsByStatusOut

router = APIRouter(prefix="/reports", tags=["reports"])

# Only agents and admins can see cross-ticket analytics.
_agent_or_admin = require_role("agent", "admin")


@router.get("/tickets-by-status", response_model=list[TicketsByStatusOut])
def tickets_by_status(db: Session = Depends(get_db), _=Depends(_agent_or_admin)):
    rows = (
        db.query(Ticket.status, func.count(Ticket.id))
        .group_by(Ticket.status)
        .all()
    )
    return [TicketsByStatusOut(status=status, count=count) for status, count in rows]


@router.get("/avg-resolution-time", response_model=list[AvgResolutionTimeOut])
def avg_resolution_time(db: Session = Depends(get_db), _=Depends(_agent_or_admin)):
    """
    Average time (in hours) tickets spent open before being closed, grouped
    by the agent who closed them. Computed from status_history so it reflects
    the actual audit trail rather than a snapshot field on the ticket.
    """
    closed_events = (
        db.query(StatusHistory)
        .filter(StatusHistory.new_status == "closed")
        .all()
    )

    by_agent: dict[str, list[float]] = {}
    for event in closed_events:
        ticket = db.query(Ticket).filter(Ticket.id == event.ticket_id).first()
        if ticket is None:
            continue
        created_at = ticket.created_at
        closed_at = event.changed_at
        if created_at is None or closed_at is None:
            continue
        hours = (closed_at - created_at).total_seconds() / 3600
        agent_key = f"agent_{event.changed_by}"
        by_agent.setdefault(agent_key, []).append(hours)

    return [
        AvgResolutionTimeOut(
            group=agent_key,
            avg_hours=round(sum(hours) / len(hours), 2) if hours else None,
            resolved_count=len(hours),
        )
        for agent_key, hours in by_agent.items()
    ]


@router.get("/overdue", response_model=list[OverdueTicketOut])
def overdue(hours: float = 24, db: Session = Depends(get_db), _=Depends(_agent_or_admin)):
    """Tickets that have spent longer than `hours` in their current status."""
    now = datetime.now(timezone.utc)
    open_tickets = db.query(Ticket).filter(Ticket.status != "closed").all()

    result = []
    for ticket in open_tickets:
        reference_time = ticket.updated_at or ticket.created_at
        if reference_time is None:
            continue
        if reference_time.tzinfo is None:
            reference_time = reference_time.replace(tzinfo=timezone.utc)
        hours_in_status = (now - reference_time).total_seconds() / 3600
        if hours_in_status >= hours:
            result.append(
                OverdueTicketOut(
                    id=ticket.id,
                    title=ticket.title,
                    status=ticket.status,
                    hours_in_status=round(hours_in_status, 2),
                )
            )
    return result
