import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120, protected_paths: List[str] = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.protected_paths = protected_paths or ["/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/analysis"]
        self.client_records: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        path = request.url.path
        is_protected = any(path.startswith(p) for p in self.protected_paths)

        if is_protected:
            client_host = request.client.host if request.client else None
            if not client_host or client_host in ("testserver", "localhost", "127.0.0.1"):
                return await call_next(request)
            client_ip = client_host
            now = time.time()
            window_start = now - 60

            # Filter timestamps outside the 1 minute window
            timestamps = [ts for ts in self.client_records[client_ip] if ts > window_start]
            self.client_records[client_ip] = timestamps

            limit = 20 if "auth" in path else self.requests_per_minute
            if len(timestamps) >= limit:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests. Please try again later."
                        }
                    }
                )
            self.client_records[client_ip].append(now)

        return await call_next(request)
