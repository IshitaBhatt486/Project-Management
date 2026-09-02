from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user
from backend.core.config import settings
from backend.core.security import AUTH_COOKIE_NAME, create_session_token
from backend.db.models import User
from backend.db.session import get_db
from backend.schemas.auth import LoginInput, RegisterInput, UserRead
from backend.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


def _cookie_is_secure(request: Request) -> bool:
    return settings.session_cookie_secure and request.url.scheme == "https"


def _set_session_cookie(response: Response, user_id: int, request: Request) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=create_session_token(user_id),
        max_age=settings.session_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=_cookie_is_secure(request),
        samesite="lax",
        path="/",
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterInput,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> UserRead:
    user = service.register(db, payload)
    if not user:
        raise HTTPException(status_code=409, detail="An account with that email already exists")
    _set_session_cookie(response, user.id, request)
    return user


@router.post("/login", response_model=UserRead)
def login(
    payload: LoginInput,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> UserRead:
    user = service.authenticate(db, payload)
    if not user:
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    _set_session_cookie(response, user.id, request)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response) -> None:
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        httponly=True,
        secure=_cookie_is_secure(request),
        samesite="lax",
        path="/",
    )


@router.get("/me", response_model=UserRead)
def current_user(
    _request: Request, user: User = Depends(get_current_user)
) -> UserRead:
    return user