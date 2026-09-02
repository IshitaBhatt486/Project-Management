from fastapi import APIRouter, HTTPException

from backend.db.session import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/healthz")
def health_check() -> dict[str, str]:
    try:
        check_database_connection()
    except Exception as error:
        raise HTTPException(status_code=503, detail="Database unavailable") from error
    return {"status": "ok"}