import enum

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    agent = "agent"
    client = "client"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'agent', 'client')", name="ck_users_role"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False, default=UserRole.client.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    created_tickets = relationship(
        "Ticket", back_populates="creator", foreign_keys="Ticket.created_by"
    )
    assigned_tickets = relationship(
        "Ticket", back_populates="assignee", foreign_keys="Ticket.assigned_to"
    )
    comments = relationship("Comment", back_populates="author")
