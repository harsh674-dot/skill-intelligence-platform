import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)


@router.get(
    "",
    response_model=list[AuditLogResponse],
)
def get_audit_logs(
    user_id: uuid.UUID | None = Query(None, description="Filter by user ID"),
    action: str | None = Query(None, description="Filter by action"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Admin-only: Retrieve audit logs with optional filters.
    """
    statement = select(AuditLog).order_by(desc(AuditLog.created_at))

    if user_id is not None:
        statement = statement.where(AuditLog.user_id == user_id)

    if action is not None:
        statement = statement.where(AuditLog.action == action)

    statement = statement.limit(limit)

    logs = db.scalars(statement).all()

    return [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
            ip_address=log.ip_address,
            created_at=log.created_at,
        )
        for log in logs
    ]
