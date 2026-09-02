from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from backend.core.config import settings

ALGORITHM = "HS256"
AUTH_COOKIE_NAME = "workbench_session"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"), password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def create_session_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(days=settings.session_expire_days),
    }
    return jwt.encode(payload, settings.session_secret, algorithm=ALGORITHM)


def decode_session_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.session_secret, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        return int(subject) if subject is not None else None
    except (jwt.InvalidTokenError, TypeError, ValueError):
        return None