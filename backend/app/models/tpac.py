from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TPACApprovalRequest(BaseModel):
    id: str
    course_id: str
    requested_by: str
    status: str = Field(..., description="PENDING, APPROVED, REJECTED")
    request_date: datetime = Field(default_factory=datetime.utcnow)
    approval_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    comments: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "req-001",
                "course_id": "course-123",
                "requested_by": "user-456",
                "status": "PENDING",
                "request_date": "2026-09-16T12:00:00Z"
            }
        }

class TPACApprovalResponse(BaseModel):
    message: str
    approval_request: TPACApprovalRequest
