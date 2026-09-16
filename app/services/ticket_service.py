from sqlalchemy.orm import Session

from app.models.status_history import StatusHistory
from app.models.ticket import Ticket
from app.schemas.ticket import TicketUpdate


def update_ticket(db: Session, ticket: Ticket, data: TicketUpdate, changed_by: int) -> Ticket:
    """
    Applies changes to a ticket. If the status changes, records the transition
    in status_history in the same transaction as the update, so the audit
    trail can never drift from the ticket's actual status changes.
    """
    old_status = ticket.status

    if data.priority is not None:
        ticket.priority = data.priority.value
    if data.category_id is not None:
        ticket.category_id = data.category_id
    if data.assigned_to is not None:
        ticket.assigned_to = data.assigned_to

    if data.status is not None and data.status.value != old_status:
        ticket.status = data.status.value
        db.add(
            StatusHistory(
                ticket_id=ticket.id,
                old_status=old_status,
                new_status=data.status.value,
                changed_by=changed_by,
            )
        )

    db.commit()
    db.refresh(ticket)
    return ticket
