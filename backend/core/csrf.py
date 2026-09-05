from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from backend.core.config import settings


class CSRFMiddleware(BaseHTTPMiddleware):
    """Reject cross-site browser mutations using Fetch Metadata and Origin headers."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method in {"GET", "HEAD", "OPTIONS", "TRACE"}:
            return await call_next(request)

        fetch_site = request.headers.get("sec-fetch-site")
        if fetch_site == "cross-site":
            return self._rejected()

        origin = request.headers.get("origin")
        if origin and origin not in self._allowed_origins(request):
            return self._rejected()
        return await call_next(request)

    @staticmethod
    def _allowed_origins(request: Request) -> set[str]:
        request_origin = f"{request.url.scheme}://{request.url.netloc}"
        return {
            request_origin,
            *(origin.rstrip("/") for origin in settings.cors_origins),
        }

    @staticmethod
    def _rejected() -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"detail": "Cross-site request rejected"},
        )
