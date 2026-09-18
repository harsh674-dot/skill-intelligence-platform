import json
import time
from collections import defaultdict
from collections.abc import Callable, Generator

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import SessionLocal
from app.models.audit_log import AuditLog

_rate_limits: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_WINDOW: float = 60.0
_RATE_LIMIT_MAX: int = 100


def is_rate_limited(key: str) -> bool:
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW
    _rate_limits[key] = [t for t in _rate_limits[key] if t > window_start]
    if len(_rate_limits[key]) >= _RATE_LIMIT_MAX:
        return True
    return False


def record_request(key: str) -> None:
    _rate_limits[key].append(time.time())


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        response: Response = await call_next(request)

        if request.url.path.startswith("/api/") and request.url.path != "/api/":
            try:
                body_bytes = await request.body()
                body_str = body_bytes.decode("utf-8")[:500] if body_bytes else None
            except Exception:
                body_str = None

            user_id: str | None = None
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                try:
                    import jwt
                    from app.security import SECRET_KEY, ALGORITHM
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    user_id = payload.get("sub")
                except Exception:
                    pass

            ip_address: str | None = (
                request.headers.get("X-Forwarded-For", "")
                or request.headers.get("X-Real-IP", "")
                or ""
            ).split(",")[0].strip() or None

            action = f"{request.method} {request.url.path}"

            details = None
            if body_str and request.method in ("POST", "PUT", "PATCH", "DELETE"):
                details = {"body": body_str}

            def _log_audit() -> None:
                db = SessionLocal()
                try:
                    audit = AuditLog(
                        user_id=user_id if user_id else None,
                        action=action,
                        entity_type=None,
                        entity_id=None,
                        details=details,
                        ip_address=ip_address,
                    )
                    db.add(audit)
                    db.commit()
                except Exception:
                    db.rollback()
                finally:
                    db.close()

            try:
                _log_audit()
            except Exception:
                pass

        return response
