import json
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class HealthCheckMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        response: Response = await call_next(request)

        if request.url.path == "/health":
            response.headers["X-Health-Check"] = "ok"
            response.headers["Cache-Control"] = "no-store"

        return response
