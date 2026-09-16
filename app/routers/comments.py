from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.ticket import add_comment, get_ticket
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut

router = APIRouter(prefix="/tickets/{ticket_id}/comments", tags=["comments"])


@router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create(
    ticket_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if current_user.role == "client" and ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot comment on this ticket")
    return add_comment(db, ticket_id, current_user.id, data)
