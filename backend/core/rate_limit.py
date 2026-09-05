from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """Small process-local limiter; replace with Redis when running multiple workers."""

    def __init__(self, attempts: int, window_seconds: int) -> None:
        self.attempts = attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            timestamps = self._attempts[key]
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if len(timestamps) >= self.attempts:
                retry_after = max(1, int(self.window_seconds - (now - timestamps[0])))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many authentication attempts. Please try again shortly.",
                    headers={"Retry-After": str(retry_after)},
                )
            timestamps.append(now)


auth_rate_limiter = SlidingWindowRateLimiter(attempts=10, window_seconds=60)


def rate_limit_auth(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    auth_rate_limiter.check(client)
