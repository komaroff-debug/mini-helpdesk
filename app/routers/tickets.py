from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.ticket import create_ticket, get_ticket, list_tickets
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.ticket import (
    TicketCreate,
    TicketDetailOut,
    TicketListOut,
    TicketOut,
    TicketUpdate,
)
from app.services.ticket_service import update_ticket

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create(
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_ticket(db, data, created_by=current_user.id)


@router.get("", response_model=TicketListOut)
def list_all(
    status_: str | None = None,
    priority: str | None = None,
    category_id: int | None = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = list_tickets(
        db,
        requester_id=current_user.id,
        requester_role=current_user.role,
        status=status_,
        priority=priority,
        category_id=category_id,
        page=page,
        size=size,
    )
    return TicketListOut(items=items, total=total, page=page, size=size)


def _get_ticket_or_404(db: Session, ticket_id: int):
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


def _ensure_can_view(ticket, current_user: User):
    if current_user.role == "client" and ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot access this ticket")


@router.get("/{ticket_id}", response_model=TicketDetailOut)
def get_one(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = _get_ticket_or_404(db, ticket_id)
    _ensure_can_view(ticket, current_user)
    return ticket


@router.patch("/{ticket_id}", response_model=TicketOut)
def update(
    ticket_id: int,
    data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "client":
        raise HTTPException(
            status_code=403, detail="Clients cannot update tickets"
        )
    ticket = _get_ticket_or_404(db, ticket_id)
    return update_ticket(db, ticket, data, changed_by=current_user.id)
