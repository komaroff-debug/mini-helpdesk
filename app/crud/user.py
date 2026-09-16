from sqlalchemy.orm import Session

from app.models.user import User
from app.security import hash_password
from app.schemas.user import UserRegister


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, data: UserRegister, role: str = "client") -> User:
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
