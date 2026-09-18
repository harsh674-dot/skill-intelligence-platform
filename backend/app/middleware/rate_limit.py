import time
from collections import defaultdict
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import run_in_threadpool

from app.middleware.audit import is_rate_limited, record_request


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        if request.url.path.startswith("/api/"):
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                try:
                    import jwt
                    from app.security import SECRET_KEY, ALGORITHM
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    user_id = payload.get("sub", "anonymous")
                except Exception:
                    user_id = request.client.host if request.client else "anonymous"
            else:
                user_id = request.client.host if request.client else "anonymous"

            key = f"rate_limit:{user_id}"

            if is_rate_limited(key):
                return Response(
                    json.dumps({"detail": "Too many requests. Please try again later."}),
                    status_code=429,
                    headers={
                        "Retry-After": str(int(60)),
                        "Content-Type": "application/json",
                    },
                )

            record_request(key)

        return await call_next(request)
