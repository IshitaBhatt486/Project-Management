from sqlalchemy.orm import Session

from backend.core.security import hash_password, verify_password
from backend.db.models import User
from backend.repositories.user import UserRepository
from backend.schemas.auth import LoginInput, RegisterInput


class AuthService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    def register(self, db: Session, payload: RegisterInput) -> User | None:
        email = str(payload.email).lower()
        if self.repository.get_by_email(db, email):
            return None
        return self.repository.create(db, payload, hash_password(payload.password))

    def authenticate(self, db: Session, payload: LoginInput) -> User | None:
        user = self.repository.get_by_email(db, str(payload.email).lower())
        if not user or not verify_password(payload.password, user.password_hash):
            return None
        return user