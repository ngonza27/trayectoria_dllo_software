import time
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class FixedWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int, clock=time.time):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clock = clock
        self._lock = Lock()
        self._counters: dict[str, tuple[int, float]] = {}

    def check(self, key: str) -> tuple[bool, int]:
        now = self._clock()
        with self._lock:
            count, window_start = self._counters.get(key, (0, now))
            if now - window_start >= self.window_seconds:
                count, window_start = 0, now
            count += 1
            self._counters[key] = (count, window_start)
            allowed = count <= self.max_requests
            retry_after = max(0, round(self.window_seconds - (now - window_start)))
            return allowed, retry_after


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: FixedWindowRateLimiter, protected_paths: set[str]):
        super().__init__(app)
        self.limiter = limiter
        self.protected_paths = protected_paths

    @staticmethod
    def _client_ip(request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path not in self.protected_paths:
            return await call_next(request)

        client_ip = self._client_ip(request)
        key = f"{client_ip}:{request.url.path}"
        allowed, retry_after = self.limiter.check(key)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"},
                headers={"Retry-After": str(retry_after)},
            )
        return await call_next(request)
