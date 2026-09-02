from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import User
from backend.schemas.auth import RegisterInput


class UserRepository:
    def get(self, db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.scalar(select(User).where(User.email == email))

    def create(self, db: Session, payload: RegisterInput, password_hash: str) -> User:
        user = User(
            name=payload.name.strip(),
            email=str(payload.email).lower(),
            password_hash=password_hash,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user