from fastapi import APIRouter, Response
from pydantic import BaseModel
from sqlalchemy import text

from app.database import SessionLocal

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


class HealthResponse(BaseModel):
    status: str
    service: str = "skill-intelligence-platform"
    version: str = "1.0.0"
    database: str | None = None


@router.get("", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok")


@router.get("/ready")
def readiness_check():
    checks: dict[str, bool] = {
        "service": True,
    }

    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False
    finally:
        db.close()

    all_ok = all(checks.values())
    status = "ready" if all_ok else "not_ready"

    return {"status": status, **checks}


@router.get("/database")
def database_health_check():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected",
        }

    finally:
        db.close()
