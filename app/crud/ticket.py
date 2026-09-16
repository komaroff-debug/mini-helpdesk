from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.ticket import Ticket
from app.schemas.comment import CommentCreate
from app.schemas.ticket import TicketCreate


def create_ticket(db: Session, data: TicketCreate, created_by: int) -> Ticket:
    ticket = Ticket(
        title=data.title,
        description=data.description,
        category_id=data.category_id,
        priority=data.priority.value,
        created_by=created_by,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def list_tickets(
    db: Session,
    *,
    requester_id: int,
    requester_role: str,
    status: str | None = None,
    priority: str | None = None,
    category_id: int | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Ticket], int]:
    query = db.query(Ticket)

    # clients only ever see their own tickets
    if requester_role == "client":
        query = query.filter(Ticket.created_by == requester_id)

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category_id:
        query = query.filter(Ticket.category_id == category_id)

    total = query.with_entities(func.count(Ticket.id)).scalar() or 0
    items = (
        query.order_by(Ticket.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return items, total


def add_comment(db: Session, ticket_id: int, author_id: int, data: CommentCreate) -> Comment:
    comment = Comment(ticket_id=ticket_id, author_id=author_id, body=data.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
