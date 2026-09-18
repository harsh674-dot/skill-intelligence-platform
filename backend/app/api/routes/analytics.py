from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin

from app.services.predictive_analytics import (
    predict_future_skill_gaps,
    predict_training_success_rate
)

router = APIRouter(tags=["analytics"])

@router.get("/analytics/predict/skill-gaps", response_model=List[Dict[str, Any]])
def get_predicted_skill_gaps(department_id: str = None, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """
    Predict future skill gaps based on historical organizational data.
    """
    return predict_future_skill_gaps(db, department_id)

@router.get("/analytics/predict/course-success", response_model=Dict[str, Any])
def get_predicted_course_success(course_id: str, user_id: str, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """
    Predict the likelihood of a user successfully completing a course.
    """
    return predict_training_success_rate(db, course_id, user_id)
