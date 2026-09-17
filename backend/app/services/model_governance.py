import json
import hashlib
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.ai_ml import ModelGovernance
from app.models.audit_log import AuditLog
from app.models.user import User

logger = logging.getLogger(__name__)


class ModelGovernanceService:
    """
    Model Governance (Section 4.5):
    All LLM outputs are logged, versioned, and auditable.
    """

    def __init__(self, db: Session):
        self.db = db

    def log_inference(
        self,
        model_name: str,
        model_version: str,
        model_type: str,
        input_text: str,
        output_summary: dict,
        latency_ms: Optional[float] = None,
        user_id: Optional[str] = None,
    ) -> ModelGovernance:
        """Log an LLM inference for audit trail."""
        input_hash = hashlib.sha256(input_text.encode()).hexdigest()

        record = ModelGovernance(
            model_name=model_name,
            model_version=model_version,
            model_type=model_type,
            input_hash=input_hash,
            output_summary=output_summary,
            latency_ms=latency_ms,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        logger.info(
            f"Model governance logged: {model_name} v{model_version} "
            f"(type={model_type}, hash={input_hash[:12]}...)"
        )

        return record

    def get_log(
        self,
        governance_id: str,
    ) -> Optional[ModelGovernance]:
        return self.db.get(ModelGovernance, governance_id)

    def list_logs(
        self,
        model_name: Optional[str] = None,
        model_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[ModelGovernance]:
        stmt = select(ModelGovernance).order_by(ModelGovernance.created_at.desc())

        if model_name:
            stmt = stmt.where(ModelGovernance.model_name == model_name)
        if model_type:
            stmt = stmt.where(ModelGovernance.model_type == model_type)

        stmt = stmt.limit(limit)
        return self.db.scalars(stmt).all()

    def approve_inference(
        self,
        governance_id: str,
        reviewed_by: str,
        notes: Optional[str] = None,
    ) -> ModelGovernance:
        record = self.get_log(governance_id)
        if not record:
            raise ValueError(f"Governance record not found: {governance_id}")

        record.is_approved = True
        record.reviewed_by = reviewed_by
        record.review_notes = notes
        self.db.commit()
        self.db.refresh(record)
        return record

    def reject_inference(
        self,
        governance_id: str,
        reviewed_by: str,
        notes: Optional[str] = None,
    ) -> ModelGovernance:
        record = self.get_log(governance_id)
        if not record:
            raise ValueError(f"Governance record not found: {governance_id}")

        record.is_approved = False
        record.reviewed_by = reviewed_by
        record.review_notes = notes
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_audit_trail(
        self,
        entity_type: str,
        entity_id: str,
    ) -> list[AuditLog]:
        """Get audit trail for a specific entity."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
        )
        return self.db.scalars(stmt).all()
