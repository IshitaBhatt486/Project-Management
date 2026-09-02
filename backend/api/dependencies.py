from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.core.security import AUTH_COOKIE_NAME, decode_session_token
from backend.db.models import User
from backend.db.session import get_db
from backend.repositories.user import UserRepository

user_repository = UserRepository()


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    token = request.cookies.get(AUTH_COOKIE_NAME)
    user_id = decode_session_token(token) if token else None
    user = user_repository.get(db, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user