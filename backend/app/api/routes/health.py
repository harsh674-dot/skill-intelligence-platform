from fastapi import APIRouter
from sqlalchemy import text

from app.database import SessionLocal

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check():
    return {
        "status": "ok",
        "service": "skill-intelligence-platform",
    }


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