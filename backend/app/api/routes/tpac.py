from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.tpac_request import TPACRequest
from app.models.tpac import TPACApprovalRequest, TPACApprovalResponse

router = APIRouter(tags=["tpac"])

@router.post("/tpac/request", response_model=TPACApprovalResponse)
def submit_tpac_request(course_id: str, requested_by: str, db: Session = Depends(get_db)):
    """
    Submit a course for TPAC approval.
    """
    request_id = f"req-{uuid.uuid4().hex[:8]}"
    new_request = TPACRequest(
        id=request_id,
        course_id=course_id,
        requested_by=requested_by,
        status="PENDING",
        request_date=datetime.utcnow()
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return TPACApprovalResponse(
        message="TPAC approval request submitted successfully",
        approval_request=TPACApprovalRequest(
            id=new_request.id,
            course_id=new_request.course_id,
            requested_by=new_request.requested_by,
            status=new_request.status,
            request_date=new_request.request_date,
            approval_date=new_request.approval_date,
            approved_by=new_request.approved_by,
            comments=new_request.comments
        )
    )

@router.get("/tpac/requests", response_model=List[TPACApprovalRequest])
def get_tpac_requests(status: str = None, db: Session = Depends(get_db)):
    """
    Get all TPAC approval requests, optionally filtered by status.
    """
    stmt = select(TPACRequest)
    if status:
        stmt = stmt.where(TPACRequest.status == status)
    
    db_requests = db.scalars(stmt).all()
    
    return [
        TPACApprovalRequest(
            id=req.id,
            course_id=req.course_id,
            requested_by=req.requested_by,
            status=req.status,
            request_date=req.request_date,
            approval_date=req.approval_date,
            approved_by=req.approved_by,
            comments=req.comments
        )
        for req in db_requests
    ]

@router.put("/tpac/request/{request_id}/approve", response_model=TPACApprovalResponse)
def approve_tpac_request(request_id: str, approved_by: str, comments: str = None, db: Session = Depends(get_db)):
    """
    Approve a TPAC request.
    """
    req = db.get(TPACRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Cannot approve request with status {req.status}")
        
    req.status = "APPROVED"
    req.approval_date = datetime.utcnow()
    req.approved_by = approved_by
    req.comments = comments
    
    db.commit()
    db.refresh(req)
    
    return TPACApprovalResponse(
        message="TPAC request approved successfully",
        approval_request=TPACApprovalRequest(
            id=req.id,
            course_id=req.course_id,
            requested_by=req.requested_by,
            status=req.status,
            request_date=req.request_date,
            approval_date=req.approval_date,
            approved_by=req.approved_by,
            comments=req.comments
        )
    )

@router.put("/tpac/request/{request_id}/reject", response_model=TPACApprovalResponse)
def reject_tpac_request(request_id: str, rejected_by: str, comments: str, db: Session = Depends(get_db)):
    """
    Reject a TPAC request.
    """
    req = db.get(TPACRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Cannot reject request with status {req.status}")
        
    req.status = "REJECTED"
    req.approval_date = datetime.utcnow()
    req.approved_by = rejected_by
    req.comments = comments
    
    db.commit()
    db.refresh(req)
    
    return TPACApprovalResponse(
        message="TPAC request rejected successfully",
        approval_request=TPACApprovalRequest(
            id=req.id,
            course_id=req.course_id,
            requested_by=req.requested_by,
            status=req.status,
            request_date=req.request_date,
            approval_date=req.approval_date,
            approved_by=req.approved_by,
            comments=req.comments
        )
    )
